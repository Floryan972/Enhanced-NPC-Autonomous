from pathlib import Path
import json
from typing import Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class PlayerAgent:
    def __init__(self, config_path: str = "config/player_control.json"):
        self.config = self._load_config(config_path)
        self.model_path = Path("models/Qwen2-7B-Instruct-v0.6.Q4_K_M.gguf")
        self.context_history = []
        self.max_history = 10
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Utilisation d'un modèle plus léger pour les tests
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2")
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/phi-2")
        self.model.to(self.device)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Charge la configuration depuis un fichier JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur de chargement config: {e}")
            return {}

    def _validate_game_state(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Valide et nettoie l'état du jeu"""
        required_keys = ['health', 'position', 'inventory', 'nearby_entities']
        
        validated_state = game_state.copy()
        for key in required_keys:
            if key not in validated_state:
                validated_state[key] = self.config.get(f"default_{key}", {})
        
        return validated_state

    def get_action(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Détermine la meilleure action basée sur l'état du jeu et le contexte"""
        game_state = self._validate_game_state(game_state)
        
        # Préparation du prompt pour le modèle
        context = self._prepare_context(game_state)
        response = self._query_model(context)
        
        # Analyse de la réponse et conversion en action
        action = self._parse_model_response(response)
        
        # Mise à jour de l'historique
        self._update_history(game_state, action)
        
        return action

    def _prepare_context(self, game_state: Dict[str, Any]) -> str:
        """Prépare le contexte pour le modèle"""
        context = f"""État actuel:
- Santé: {game_state['health']}
- Position: {game_state['position']}
- Entités proches: {len(game_state['nearby_entities'])}
- Inventaire: {len(game_state['inventory'])} objets

Historique récent:
{self._format_history()}

Quelle action prendre ?"""
        return context

    def _query_model(self, prompt: str) -> str:
        """Interroge le modèle"""
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=200,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_p=0.9
                )
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            print(f"Erreur modèle: {e}")
            return ""

    def _parse_model_response(self, response: str) -> Dict[str, Any]:
        """Analyse la réponse du modèle et la convertit en action"""
        try:
            # Analyse simple - à améliorer selon le format de réponse
            action_types = ['movement', 'combat', 'interaction', 'inventory']
            for action_type in action_types:
                if action_type in response.lower():
                    return {
                        'type': action_type,
                        'parameters': self._extract_parameters(response)
                    }
            return {'type': 'idle', 'parameters': {}}
        except Exception as e:
            print(f"Erreur analyse réponse: {e}")
            return {'type': 'idle', 'parameters': {}}

    def _extract_parameters(self, response: str) -> Dict[str, Any]:
        """Extrait les paramètres de la réponse"""
        params = {}
        # Logique d'extraction à personnaliser selon le format de réponse
        return params

    def _update_history(self, state: Dict[str, Any], action: Dict[str, Any]):
        """Met à jour l'historique des actions"""
        self.context_history.append({
            'state': state,
            'action': action
        })
        if len(self.context_history) > self.max_history:
            self.context_history.pop(0)

    def _format_history(self) -> str:
        """Formate l'historique pour le contexte"""
        if not self.context_history:
            return "Pas d'historique"
        
        history = []
        for entry in self.context_history[-3:]:  # Dernières 3 entrées
            action = entry['action']
            history.append(f"- Action: {action['type']}")
        
        return "\n".join(history)

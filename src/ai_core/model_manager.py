from pathlib import Path
import json
from typing import Dict, Optional, List
from ctransformers import AutoModelForCausalLM
import os

class ModelManager:
    def __init__(self):
        self.config_path = Path(__file__).parent / "model_configs.json"
        self.models_dir = Path(__file__).parent.parent.parent / "models"
        self.loaded_models = {}
        self.configs = self._load_configs()
        
    def _load_configs(self) -> Dict:
        """Charge les configurations des modèles"""
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def get_available_models(self) -> List[Dict]:
        """Liste tous les modèles disponibles dans le dossier models"""
        models = []
        for file in self.models_dir.glob("*.gguf"):
            model_info = {
                "name": file.stem,
                "path": str(file),
                "size": file.stat().st_size / (1024 * 1024),  # Taille en MB
                "type": self._detect_model_type(file.name)
            }
            models.append(model_info)
        return models

    def _detect_model_type(self, filename: str) -> str:
        """Détecte le type de modèle basé sur le nom du fichier"""
        filename = filename.lower()
        if "llama" in filename:
            return "llama"
        elif "mistral" in filename:
            return "mistral"
        elif "phi" in filename:
            return "phi"
        elif "gpt4all" in filename:
            return "gpt4all"
        return "llama"  # Type par défaut

    def load_model(self, model_name: str = None, role: str = "npc_dialogue") -> Optional[AutoModelForCausalLM]:
        """Charge un modèle spécifique ou le premier modèle disponible"""
        available_models = self.get_available_models()
        
        if not available_models:
            raise ValueError("Aucun modèle trouvé dans le dossier models/")
        
        # Sélection du modèle
        if model_name:
            model_info = next((m for m in available_models if m["name"] == model_name), None)
            if not model_info:
                raise ValueError(f"Modèle {model_name} non trouvé")
        else:
            model_info = available_models[0]
            print(f"Utilisation automatique du modèle: {model_info['name']}")
        
        # Configuration du modèle
        model_type = model_info["type"]
        model_config = self.configs["model_types"][model_type]
        role_config = self.configs["role_configs"][role]
        
        # Chargement du modèle
        if model_info["path"] not in self.loaded_models:
            self.loaded_models[model_info["path"]] = AutoModelForCausalLM.from_pretrained(
                model_info["path"],
                model_type=model_config["model_type"],
                gpu_layers=model_config["parameters"]["gpu_layers"]
            )
        
        return self.loaded_models[model_info["path"]]

    def format_prompt(self, prompt: str, model_type: str, role: str) -> str:
        """Formate le prompt selon le type de modèle et le rôle"""
        model_config = self.configs["model_types"][model_type]
        role_config = self.configs["role_configs"][role]
        
        # Combine le prompt système et l'entrée utilisateur
        full_prompt = f"{role_config['system_prompt']}\n\n{prompt}"
        
        # Applique le template spécifique au modèle
        return model_config["prompt_template"].format(prompt=full_prompt)

    def get_generation_params(self, model_type: str, role: str) -> Dict:
        """Récupère les paramètres de génération pour un type de modèle et un rôle"""
        model_config = self.configs["model_types"][model_type]
        role_config = self.configs["role_configs"][role]
        
        # Combine les paramètres du modèle et du rôle
        params = model_config["parameters"].copy()
        params.update({
            "temperature": role_config.get("temperature", params["temperature"]),
            "max_tokens": role_config.get("max_tokens", params["max_tokens"])
        })
        
        return params

    async def generate_response(self, 
                              prompt: str,
                              model_name: str = None,
                              role: str = "npc_dialogue") -> str:
        """Génère une réponse en utilisant le modèle spécifié"""
        try:
            # Charge ou récupère le modèle
            model = self.load_model(model_name, role)
            
            # Détermine le type de modèle
            model_type = self._detect_model_type(model_name if model_name else "")
            
            # Formate le prompt
            formatted_prompt = self.format_prompt(prompt, model_type, role)
            
            # Récupère les paramètres de génération
            params = self.get_generation_params(model_type, role)
            
            # Génère la réponse
            response = model(
                formatted_prompt,
                **params,
                stop=self.configs["model_types"][model_type]["stop_words"]
            )
            
            return response.strip()
            
        except Exception as e:
            print(f"Erreur lors de la génération: {str(e)}")
            return "Désolé, je ne peux pas générer de réponse pour le moment."

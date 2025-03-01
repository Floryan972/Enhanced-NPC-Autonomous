import json
import logging
import requests
from typing import Dict, Any, Optional
import time

class LLMInterface:
    """Interface avec le modèle LLM local"""

    def __init__(self, host: str = "127.0.0.1", port: int = 1234):
        self.logger = logging.getLogger(__name__)
        self.base_url = f"http://{host}:{port}"
        self.headers = {
            "Content-Type": "application/json"
        }
        self.last_call_time = 0
        self.min_call_interval = 0.1  # secondes

    def generate_response(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Génère une réponse à partir du prompt"""
        try:
            # Respect du taux limite
            current_time = time.time()
            time_since_last_call = current_time - self.last_call_time
            if time_since_last_call < self.min_call_interval:
                time.sleep(self.min_call_interval - time_since_last_call)

            # Préparation de la requête
            payload = {
                "prompt": prompt,
                "max_tokens": 150,
                "temperature": 0.7,
                "stop": ["\n\n"]
            }

            # Appel à l'API
            response = requests.post(
                f"{self.base_url}/v1/completions",
                headers=self.headers,
                json=payload,
                timeout=5
            )

            self.last_call_time = time.time()

            if response.status_code == 200:
                try:
                    result = response.json()
                    if "choices" in result and result["choices"]:
                        action_text = result["choices"][0]["text"].strip()
                        return json.loads(action_text)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Erreur de parsing JSON: {e}")
                    return None
            else:
                self.logger.error(f"Erreur API: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de réponse: {e}")
            return None

    def validate_response(self, response: Dict[str, Any]) -> bool:
        """Valide la structure de la réponse"""
        required_fields = ["action_type", "parameters"]
        valid_actions = ["movement", "combat", "interaction", "inventory"]

        if not all(field in response for field in required_fields):
            return False

        if response["action_type"] not in valid_actions:
            return False

        if not isinstance(response["parameters"], dict):
            return False

        return True

    def format_action(self, raw_action: Dict[str, Any]) -> Dict[str, Any]:
        """Formate l'action pour qu'elle soit utilisable par le système"""
        if not self.validate_response(raw_action):
            return {
                "action_type": "idle",
                "parameters": {}
            }

        # Formatage spécifique selon le type d'action
        action_type = raw_action["action_type"]
        parameters = raw_action["parameters"]

        if action_type == "movement":
            parameters = self._format_movement_parameters(parameters)
        elif action_type == "combat":
            parameters = self._format_combat_parameters(parameters)
        elif action_type == "interaction":
            parameters = self._format_interaction_parameters(parameters)
        elif action_type == "inventory":
            parameters = self._format_inventory_parameters(parameters)

        return {
            "action_type": action_type,
            "parameters": parameters
        }

    def _format_movement_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Formate les paramètres de mouvement"""
        return {
            "forward": float(params.get("forward", 0)),
            "backward": float(params.get("backward", 0)),
            "left": float(params.get("left", 0)),
            "right": float(params.get("right", 0)),
            "sprint": bool(params.get("sprint", False))
        }

    def _format_combat_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Formate les paramètres de combat"""
        return {
            "type": str(params.get("type", "shoot")),
            "target": params.get("target", None),
            "weapon": str(params.get("weapon", "primary")),
            "hold": bool(params.get("hold", False))
        }

    def _format_interaction_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Formate les paramètres d'interaction"""
        return {
            "type": str(params.get("type", "use")),
            "target": params.get("target", None),
            "duration": float(params.get("duration", 0))
        }

    def _format_inventory_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Formate les paramètres d'inventaire"""
        return {
            "type": str(params.get("type", "use")),
            "item": str(params.get("item", "")),
            "quantity": int(params.get("quantity", 1))
        }

from typing import Dict, Any, List, Optional
import numpy as np
from ..utils.logger import Logger
from ..utils.config import Config
import time

class AIManager:
    """Gestionnaire principal de l'IA des PNJ."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = Logger("AIManager")
        self.npcs = {}
        self.behaviors = {}
        self.states = {}
        self.memory = {}
        self.emotions = {}
        
    def register_npc(self, npc_id: str, npc_data: Dict[str, Any]) -> bool:
        """Enregistre un nouveau PNJ."""
        try:
            self.npcs[npc_id] = npc_data
            self.states[npc_id] = self._initialize_state(npc_data)
            self.behaviors[npc_id] = self._initialize_behaviors(npc_data)
            self.memory[npc_id] = []
            self.emotions[npc_id] = {
                "joy": 0.0,
                "trust": 0.0,
                "fear": 0.0,
                "surprise": 0.0,
                "sadness": 0.0,
                "disgust": 0.0,
                "anger": 0.0,
                "anticipation": 0.0
            }
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement du PNJ {npc_id}: {str(e)}")
            return False
            
    def update_npc(self, npc_id: str, delta_time: float):
        """Met à jour l'état d'un PNJ."""
        if npc_id not in self.npcs:
            return
            
        try:
            # Mise à jour de l'état
            current_state = self.states[npc_id]
            behaviors = self.behaviors[npc_id]
            
            # Calcul des priorités de comportement
            priorities = self._calculate_behavior_priorities(npc_id)
            
            # Sélection du comportement
            selected_behavior = self._select_behavior(priorities)
            
            # Exécution du comportement
            if selected_behavior:
                self._execute_behavior(npc_id, selected_behavior, delta_time)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du PNJ {npc_id}: {str(e)}")
            
    def get_npc_state(self, npc_id: str) -> Dict[str, Any]:
        """Récupère l'état actuel d'un PNJ."""
        return self.states.get(npc_id, {})
        
    def set_npc_state(self, npc_id: str, state: Dict[str, Any]):
        """Définit l'état d'un PNJ."""
        if npc_id in self.npcs:
            self.states[npc_id] = state
            
    def _initialize_state(self, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialise l'état d'un PNJ."""
        return {
            "health": npc_data.get("max_health", 100),
            "stamina": npc_data.get("max_stamina", 100),
            "position": npc_data.get("spawn_position", [0, 0, 0]),
            "rotation": npc_data.get("spawn_rotation", [0, 0, 0]),
            "inventory": npc_data.get("initial_inventory", {}),
            "equipment": npc_data.get("initial_equipment", {}),
            "stats": npc_data.get("base_stats", {}),
            "faction": npc_data.get("faction", "neutral"),
            "behavior_state": "idle",
            "target": None,
            "path": [],
            "actions": [],
            "memory": {},
            "emotions": {
                "fear": 0.0,
                "anger": 0.0,
                "joy": 0.5,
                "sadness": 0.0
            }
        }
        
    def _initialize_behaviors(self, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialise les comportements d'un PNJ."""
        role = npc_data.get("role", "civilian")
        
        # Comportements de base
        behaviors = {
            "idle": {
                "weight": 1.0,
                "conditions": ["no_threat", "no_task"],
                "actions": ["wait", "look_around"]
            },
            "wander": {
                "weight": 0.8,
                "conditions": ["no_threat", "no_task"],
                "actions": ["random_walk", "explore"]
            },
            "flee": {
                "weight": 2.0,
                "conditions": ["threat_nearby", "low_health"],
                "actions": ["run_from_threat", "seek_cover"]
            }
        }
        
        # Comportements spécifiques au rôle
        if role == "merchant":
            behaviors.update({
                "trade": {
                    "weight": 1.5,
                    "conditions": ["has_goods", "player_nearby"],
                    "actions": ["offer_trade", "negotiate"]
                }
            })
        elif role == "guard":
            behaviors.update({
                "patrol": {
                    "weight": 1.2,
                    "conditions": ["no_threat", "on_duty"],
                    "actions": ["follow_patrol_path", "check_surroundings"]
                },
                "combat": {
                    "weight": 2.0,
                    "conditions": ["threat_detected"],
                    "actions": ["engage_threat", "protect_area"]
                }
            })
            
        return behaviors
        
    def _calculate_behavior_priorities(self, npc_id: str) -> Dict[str, float]:
        """Calcule les priorités des comportements."""
        state = self.states[npc_id]
        behaviors = self.behaviors[npc_id]
        priorities = {}
        
        for behavior_name, behavior_data in behaviors.items():
            base_weight = behavior_data["weight"]
            
            # Facteurs d'état
            state_multiplier = self._calculate_state_multiplier(state, behavior_name)
            
            # Facteurs environnementaux
            env_multiplier = self._calculate_environment_multiplier(state, behavior_name)
            
            # Facteurs émotionnels
            emotion_multiplier = self._calculate_emotion_multiplier(state, behavior_name)
            
            # Priorité finale
            priority = base_weight * state_multiplier * env_multiplier * emotion_multiplier
            priorities[behavior_name] = priority
            
        return priorities
        
    def _calculate_state_multiplier(self, state: Dict[str, Any], behavior: str) -> float:
        """Calcule le multiplicateur basé sur l'état."""
        multiplier = 1.0
        
        if behavior == "flee":
            # Augmente la priorité si la santé est basse
            health_ratio = state["health"] / 100.0
            multiplier *= (2.0 - health_ratio)
            
        elif behavior == "combat":
            # Diminue la priorité si la santé est basse
            health_ratio = state["health"] / 100.0
            multiplier *= health_ratio
            
        return multiplier
        
    def _calculate_environment_multiplier(self, state: Dict[str, Any], behavior: str) -> float:
        """Calcule le multiplicateur basé sur l'environnement."""
        multiplier = 1.0
        
        # Facteurs environnementaux
        if "threat_nearby" in state:
            if behavior == "flee":
                multiplier *= 2.0
            elif behavior == "idle":
                multiplier *= 0.5
                
        return multiplier
        
    def _calculate_emotion_multiplier(self, state: Dict[str, Any], behavior: str) -> float:
        """Calcule le multiplicateur basé sur les émotions."""
        multiplier = 1.0
        emotions = state.get("emotions", {})
        
        if behavior == "flee":
            multiplier *= (1.0 + emotions.get("fear", 0.0))
        elif behavior == "combat":
            multiplier *= (1.0 + emotions.get("anger", 0.0))
            
        return multiplier
        
    def _select_behavior(self, priorities: Dict[str, float]) -> str:
        """Sélectionne le comportement avec la plus haute priorité."""
        if not priorities:
            return None
            
        return max(priorities.items(), key=lambda x: x[1])[0]
        
    def _execute_behavior(self, npc_id: str, behavior: str, delta_time: float):
        """Exécute le comportement sélectionné."""
        if behavior not in self.behaviors[npc_id]:
            return
            
        behavior_data = self.behaviors[npc_id][behavior]
        actions = behavior_data["actions"]
        
        for action in actions:
            try:
                self._execute_action(npc_id, action, delta_time)
            except Exception as e:
                self.logger.error(f"Erreur lors de l'exécution de l'action {action} pour le PNJ {npc_id}: {str(e)}")
                
    def _execute_action(self, npc_id: str, action: str, delta_time: float):
        """Exécute une action spécifique."""
        state = self.states[npc_id]
        
        if action == "wait":
            # Mise à jour du temps d'attente
            pass
            
        elif action == "look_around":
            # Rotation aléatoire
            rotation = state["rotation"]
            rotation[1] += np.random.uniform(-30, 30) * delta_time
            state["rotation"] = rotation
            
        elif action == "random_walk":
            # Déplacement aléatoire
            position = state["position"]
            direction = np.random.uniform(-1, 1, 3)
            direction /= np.linalg.norm(direction)
            position += direction * 2 * delta_time
            state["position"] = position
            
        # Mise à jour de l'état
        self.states[npc_id] = state
        
    def handle_npc_action(self, event: Any) -> None:
        """Gère une action de PNJ"""
        try:
            action_data = event.data
            npc_id = action_data.get("npc_id")
            action_type = action_data.get("action_type")
            
            if not npc_id or not action_type:
                self.logger.error("Données d'action invalides")
                return
                
            if npc_id not in self.npcs:
                self.logger.error(f"PNJ non trouvé: {npc_id}")
                return
                
            # Exécuter l'action
            self._execute_action(npc_id, action_type, action_data)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de l'action: {str(e)}")
            
    def update(self, delta_time: float) -> None:
        """Met à jour l'état de l'IA"""
        try:
            for npc_id in self.npcs:
                self._update_npc(npc_id, delta_time)
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'IA: {str(e)}")
            
    def _update_npc(self, npc_id: str, delta_time: float) -> None:
        """Met à jour un PNJ"""
        try:
            # Mettre à jour l'état
            self._update_state(npc_id, delta_time)
            
            # Sélectionner le meilleur comportement
            behavior = self._select_behavior(npc_id)
            
            if behavior:
                # Exécuter le comportement
                self._execute_behavior(npc_id, behavior, delta_time)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du PNJ {npc_id}: {str(e)}")
            
    def _update_state(self, npc_id: str, delta_time: float) -> None:
        """Met à jour l'état d'un PNJ"""
        try:
            state = self.states[npc_id]
            
            # Régénération naturelle
            state["health"] = min(100, state["health"] + 0.1)
            state["stamina"] = min(100, state["stamina"] + 0.2)
            
            # TODO: Mettre à jour d'autres aspects de l'état
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'état du PNJ {npc_id}: {str(e)}")
            
    def _select_behavior(self, npc_id: str) -> Optional[str]:
        """Sélectionne le meilleur comportement pour un PNJ"""
        try:
            state = self.states[npc_id]
            behaviors = self.behaviors[npc_id]
            
            # Calculer les priorités
            priorities = {}
            for behavior, base_priority in behaviors.items():
                priority = self._calculate_priority(state, behavior, base_priority)
                priorities[behavior] = priority
                
            # Sélectionner le comportement avec la plus haute priorité
            if priorities:
                return max(priorities.items(), key=lambda x: x[1])[0]
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sélection du comportement pour le PNJ {npc_id}: {str(e)}")
            return None
            
    def _calculate_priority(self, state: Dict[str, Any], behavior: str, base_priority: float) -> float:
        """Calcule la priorité d'un comportement"""
        try:
            # Facteurs de modification de la priorité
            modifiers = {
                "idle": 1.0,
                "wander": 1.0 if state["stamina"] > 30 else 0.5,
                "interact": 1.2 if state["target"] else 0.8,
                "combat": 1.5 if state["health"] > 50 else 0.5,
                "flee": 2.0 if state["health"] < 30 else 0.1
            }
            
            return base_priority * modifiers.get(behavior, 1.0)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul de la priorité: {str(e)}")
            return 0.0
            
    def _execute_behavior(self, npc_id: str, behavior: str, delta_time: float) -> None:
        """Exécute un comportement"""
        try:
            state = self.states[npc_id]
            
            # Actions par comportement
            actions = {
                "idle": ["stand", "look_around"],
                "wander": ["walk_random"],
                "interact": ["face_target", "talk"],
                "combat": ["equip_weapon", "attack"],
                "flee": ["run_from_target"]
            }
            
            # Exécuter les actions
            for action in actions.get(behavior, []):
                self._execute_action(npc_id, action, delta_time)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution du comportement: {str(e)}")
            
    def _execute_action(self, npc_id: str, action: str, delta_time: float) -> None:
        """Exécute une action"""
        try:
            state = self.states[npc_id]
            
            # Mettre à jour l'état en fonction de l'action
            if action == "walk_random":
                # TODO: Implémenter le déplacement aléatoire
                pass
            elif action == "face_target":
                # TODO: Implémenter l'orientation vers la cible
                pass
            elif action == "talk":
                # TODO: Implémenter le dialogue
                pass
            elif action == "attack":
                # TODO: Implémenter l'attaque
                pass
            elif action == "run_from_target":
                # TODO: Implémenter la fuite
                pass
                
            self.logger.debug(f"Action exécutée pour le PNJ {npc_id}: {action}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution de l'action: {str(e)}")
            
    def get_npc_state(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """Récupère l'état d'un PNJ"""
        try:
            if npc_id not in self.npcs:
                return None
                
            return {
                "behavior": self.npcs[npc_id].get("behavior", "idle"),
                "goal": self.npcs[npc_id].get("goal"),
                "emotions": self.emotions.get(npc_id, {}),
                "memory": self.memory.get(npc_id, [])
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération de l'état du PNJ: {str(e)}")
            return None

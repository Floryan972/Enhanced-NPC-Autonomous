import json
import logging
from typing import Dict, Any, List, Tuple
from pathlib import Path
import numpy as np
import time
from dataclasses import dataclass
from .behavior_system import BehaviorSystem

@dataclass
class GameContext:
    """Contexte du jeu pour la prise de décision"""
    position: Dict[str, float]
    health: float
    stamina: float
    radiation: float
    in_combat: bool
    nearby_enemies: List[Dict[str, Any]]
    nearby_anomalies: List[Dict[str, Any]]
    current_mission: Dict[str, Any]
    inventory: Dict[str, Any]
    timestamp: float = 0.0

    def __post_init__(self):
        if self.position is None:
            self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        if self.nearby_enemies is None:
            self.nearby_enemies = []
        if self.nearby_anomalies is None:
            self.nearby_anomalies = []
        if self.current_mission is None:
            self.current_mission = {}
        if self.inventory is None:
            self.inventory = {}

class DecisionEngine:
    """Moteur de décision utilisant le LLM local pour l'analyse contextuelle"""

    def __init__(self, config_path: str = "config/player_control.json"):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.context_history: List[GameContext] = []
        self.decision_cache = {}
        self.last_decision_time = 0
        self.decision_cooldown = 0.1  # secondes
        self.behavior_system = BehaviorSystem()
        
        # Initialisation des priorités par défaut si non trouvées dans la config
        if "player_control" not in self.config:
            self.config["player_control"] = {}
        if "priorities" not in self.config["player_control"]:
            self.config["player_control"]["priorities"] = {
                "combat": 0.3,
                "survival": 0.3,
                "mission": 0.2,
                "exploration": 0.2
            }
        else:
            # S'assurer que toutes les clés de priorité existent
            default_priorities = {
                "combat": 0.3,
                "survival": 0.3,
                "mission": 0.2,
                "exploration": 0.2
            }
            for key, value in default_priorities.items():
                if key not in self.config["player_control"]["priorities"]:
                    self.config["player_control"]["priorities"][key] = value

    def analyze_situation(self, game_state: Dict[str, Any]) -> Dict[str, float]:
        """Analyse la situation actuelle et calcule les priorités"""
        
        # Validation et nettoyage des données d'entrée
        validated_state = {
            "position": game_state.get("position", {"x": 0.0, "y": 0.0, "z": 0.0}),
            "health": float(game_state.get("health", 100.0)),
            "stamina": float(game_state.get("stamina", 100.0)),
            "radiation": float(game_state.get("radiation", 0.0)),
            "in_combat": bool(game_state.get("in_combat", False)),
            "nearby_enemies": game_state.get("nearby_enemies", []),
            "nearby_anomalies": game_state.get("nearby_anomalies", []),
            "current_mission": game_state.get("current_mission", {}),
            "inventory": game_state.get("inventory", {})
        }
        
        # Mise à jour de l'état émotionnel
        self.behavior_system.update_emotional_state(validated_state)
        
        # Création du contexte actuel
        current_context = GameContext(
            position=validated_state["position"],
            health=validated_state["health"],
            stamina=validated_state["stamina"],
            radiation=validated_state["radiation"],
            in_combat=validated_state["in_combat"],
            nearby_enemies=validated_state["nearby_enemies"],
            nearby_anomalies=validated_state["nearby_anomalies"],
            current_mission=validated_state["current_mission"],
            inventory=validated_state["inventory"],
            timestamp=time.time()
        )
        
        # Mise à jour de l'historique
        self.context_history.append(current_context)
        if len(self.context_history) > 100:  # Garde les 100 derniers états
            self.context_history.pop(0)

        # Évaluation des comportements
        selected_behavior = self.behavior_system.evaluate_behaviors(game_state)
        
        if selected_behavior:
            # Utilisation des priorités du comportement sélectionné
            priorities = self._behavior_to_priorities(selected_behavior)
        else:
            # Analyse classique des menaces si aucun comportement n'est sélectionné
            threat_level = self._analyze_threats(current_context)
            resource_status = self._analyze_resources(current_context)
            mission_priority = self._analyze_mission(current_context)
            priorities = self._calculate_priorities(
                threat_level,
                resource_status,
                mission_priority
            )
        
        # Ajustement final basé sur l'état émotionnel
        emotional_state = self.behavior_system.get_emotional_state()
        priorities = self._adjust_priorities_with_emotions(priorities, emotional_state)
        
        return priorities

    def _behavior_to_priorities(self, behavior) -> Dict[str, float]:
        """Convertit un comportement en priorités"""
        base_priorities = self.config["player_control"]["priorities"].copy()
        
        # Ajustement selon l'état du comportement
        if behavior.state.name == "COMBAT":
            base_priorities["combat"] *= 1.5
            base_priorities["survival"] *= 1.3
        elif behavior.state.name == "HEALING":
            base_priorities["survival"] *= 2.0
        elif behavior.state.name == "EXPLORING":
            base_priorities["exploration"] *= 1.5
        elif behavior.state.name == "INVESTIGATING":
            base_priorities["exploration"] *= 1.3
            base_priorities["mission"] *= 1.2
        
        # Normalisation
        total = sum(base_priorities.values())
        return {k: v/total for k, v in base_priorities.items()}

    def _adjust_priorities_with_emotions(
        self,
        priorities: Dict[str, float],
        emotional_state: Dict[str, float]
    ) -> Dict[str, float]:
        """Ajuste les priorités selon l'état émotionnel"""
        adjusted = priorities.copy()
        
        # S'assurer que toutes les clés existent
        for key in ["combat", "survival", "exploration"]:
            if key not in adjusted:
                adjusted[key] = self.config["player_control"]["priorities"].get(key, 0.1)
        
        # Stress influence la survie
        if emotional_state["stress"] > 0.7:
            adjusted["survival"] *= (1 + emotional_state["stress"])
            adjusted["exploration"] *= (1 - emotional_state["stress"] * 0.5)
        
        # Peur influence le combat
        if emotional_state["fear"] > 0.6:
            adjusted["combat"] *= (1 - emotional_state["fear"] * 0.3)
            adjusted["survival"] *= (1 + emotional_state["fear"] * 0.2)
        
        # Confiance influence l'exploration
        if emotional_state["confidence"] > 0.7:
            adjusted["exploration"] *= (1 + emotional_state["confidence"] * 0.2)
            adjusted["combat"] *= (1 + emotional_state["confidence"] * 0.1)
        
        # Agressivité influence le combat
        if emotional_state["aggression"] > 0.6:
            adjusted["combat"] *= (1 + emotional_state["aggression"] * 0.3)
            adjusted["survival"] *= (1 - emotional_state["aggression"] * 0.1)
        
        # Normalisation
        total = sum(adjusted.values())
        return {k: v/total for k, v in adjusted.items()}

    def generate_decision_prompt(self, context: GameContext, priorities: Dict[str, float]) -> str:
        """Génère le prompt pour le LLM"""
        emotional_state = self.behavior_system.get_emotional_state()
        
        return f"""Situation actuelle dans STALKER 2:
- Santé: {context.health}%
- Endurance: {context.stamina}%
- Radiation: {context.radiation}
- En combat: {context.in_combat}
- Ennemis proches: {len(context.nearby_enemies)}
- Anomalies proches: {len(context.nearby_anomalies)}

État émotionnel:
- Stress: {emotional_state['stress']:.2f}
- Peur: {emotional_state['fear']:.2f}
- Confiance: {emotional_state['confidence']:.2f}
- Agressivité: {emotional_state['aggression']:.2f}

Priorités:
{json.dumps(priorities, indent=2)}

Mission actuelle:
{json.dumps(context.current_mission, indent=2)}

En tant que STALKER expérimenté dans cet état émotionnel, quelle action dois-je prendre maintenant?
Options: movement, combat, interaction, inventory
Format de réponse: {{ "action_type": "X", "parameters": {{}} }}"""

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la configuration: {e}")
            return {}

    def _analyze_threats(self, context: GameContext) -> Dict[str, float]:
        """Analyse le niveau de menace"""
        threat_level = {
            "combat": 0.0,
            "environmental": 0.0,
            "radiation": 0.0
        }

        # Menaces de combat
        if context.in_combat:
            threat_level["combat"] = 0.8
            if context.health < 50:
                threat_level["combat"] += 0.2

        # Menaces environnementales
        for anomaly in context.nearby_anomalies:
            if "position" in anomaly:
                distance = self._calculate_distance(context.position, anomaly["position"])
                danger = anomaly.get("danger_level", 0.5)
                threat_level["environmental"] += danger * (1.0 - min(1.0, distance / 100.0))

        # Menaces de radiation
        if context.radiation > 0:
            threat_level["radiation"] = min(1.0, context.radiation / 100.0)

        # Normalisation
        total = sum(threat_level.values())
        if total > 0:
            threat_level = {k: v/total for k, v in threat_level.items()}

        return threat_level

    def _analyze_resources(self, context: GameContext) -> Dict[str, float]:
        """Analyse l'état des ressources"""
        return {
            "health_status": context.health / 100,
            "stamina_status": context.stamina / 100,
            "ammo_status": self._calculate_ammo_status(context.inventory),
            "meds_status": self._calculate_meds_status(context.inventory)
        }

    def _analyze_mission(self, context: GameContext) -> Dict[str, float]:
        """Analyse les priorités de mission"""
        if not context.current_mission:
            return {"priority": 0.0, "urgency": 0.0}

        distance_to_objective = self._calculate_distance(
            context.position,
            context.current_mission.get("objective_position", context.position)
        )

        return {
            "priority": context.current_mission.get("priority", 0.5),
            "urgency": context.current_mission.get("urgency", 0.5),
            "distance_factor": 1.0 - min(1.0, distance_to_objective / 1000)
        }

    def _calculate_priorities(
        self,
        threat_level: Dict[str, float],
        resource_status: Dict[str, float],
        mission_priority: Dict[str, float]
    ) -> Dict[str, float]:
        """Calcule les priorités finales pour la prise de décision"""
        
        priorities = self.config["player_control"]["priorities"].copy()
        
        # Ajustement basé sur les menaces
        if threat_level["combat"] > 0.7:
            priorities["survival"] *= 1.5
            priorities["combat"] *= 1.3
            priorities["exploration"] *= 0.5
        
        # Ajustement basé sur les ressources
        if resource_status["health_status"] < 0.3:
            priorities["survival"] *= 2.0
            priorities["exploration"] *= 0.3
        
        # Ajustement basé sur la mission
        if mission_priority["urgency"] > 0.8:
            priorities["mission"] *= 1.4
        
        # Normalisation
        total = sum(priorities.values())
        if total > 0:
            priorities = {k: v/total for k, v in priorities.items()}
        
        return priorities

    def _calculate_distance(self, pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
        """Calcule la distance entre deux points"""
        return np.sqrt(
            (pos1["x"] - pos2["x"])**2 +
            (pos1["y"] - pos2["y"])**2 +
            (pos1["z"] - pos2["z"])**2
        )

    def _calculate_ammo_status(self, inventory: Dict[str, Any]) -> float:
        """Calcule le statut des munitions"""
        if not inventory.get("ammo"):
            return 0.0
        
        total_ammo = sum(inventory["ammo"].values())
        return min(1.0, total_ammo / 200)  # 200 balles = 100%

    def _calculate_meds_status(self, inventory: Dict[str, Any]) -> float:
        """Calcule le statut des médicaments"""
        if not inventory.get("meds"):
            return 0.0
        
        total_meds = sum(inventory["meds"].values())
        return min(1.0, total_meds / 5)  # 5 kits = 100%

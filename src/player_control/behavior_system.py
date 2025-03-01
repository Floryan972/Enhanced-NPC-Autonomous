from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Any, List, Optional
import time
import logging
from pathlib import Path

from ..npc.ai_loader import AILoader

class BehaviorState(Enum):
    IDLE = auto()
    EXPLORING = auto()
    COMBAT = auto()
    HEALING = auto()
    FLEEING = auto()

@dataclass
class Behavior:
    name: str
    state: BehaviorState
    priority: float
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    cooldown: float

class BehaviorSystem:
    def __init__(self, data_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.state_history = []
        self.max_history = 10
        self.behaviors = []
        self.last_behavior_time = {}
        self.current_state = BehaviorState.IDLE
        self.emotional_state = {
            'fear': 0.0,
            'anger': 0.0,
            'happiness': 0.5,
            'stress': 0.0,
            'confidence': 0.5  
        }
        
        # Initialisation du système
        if data_path:
            self.ai_loader = AILoader(data_path)
            self.initialize()
        else:
            self.behaviors = self._initialize_behaviors()

    def initialize(self):
        """Initialise le système de comportement"""
        try:
            # Chargement des données
            data = self.ai_loader.load_system_data("behavior")
            if data:
                self.behaviors = []
                for behavior_data in data.get("behaviors", []):
                    behavior = Behavior(
                        name=behavior_data["name"],
                        state=BehaviorState[behavior_data["state"]],
                        priority=behavior_data["priority"],
                        conditions=behavior_data["conditions"],
                        actions=behavior_data["actions"],
                        cooldown=behavior_data["cooldown"]
                    )
                    self.behaviors.append(behavior)
            else:
                self.behaviors = self._initialize_behaviors()
                
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation du système de comportement: {e}")
            self.behaviors = self._initialize_behaviors()
            return False
            
    def _initialize_behaviors(self):
        """Initialise les comportements par défaut"""
        return [
            Behavior(
                name="healing",
                state=BehaviorState.HEALING,
                priority=1.0,
                conditions={
                    "health_threshold": 0.3,
                    "has_medkit": True
                },
                actions=[
                    {
                        "type": "use_item",
                        "params": {
                            "item_type": "medkit"
                        }
                    }
                ],
                cooldown=5.0
            ),
            Behavior(
                name="combat_defensive",
                state=BehaviorState.COMBAT,
                priority=0.8,
                conditions={
                    "in_combat": True,
                    "health_threshold": 0.7
                },
                actions=[
                    {
                        "type": "movement",
                        "params": {
                            "find_cover": True
                        }
                    },
                    {
                        "type": "combat",
                        "params": {
                            "style": "defensive"
                        }
                    }
                ],
                cooldown=1.0
            ),
            Behavior(
                name="combat_aggressive",
                state=BehaviorState.COMBAT,
                priority=0.9,
                conditions={
                    "in_combat": True,
                    "health_threshold": 0.8
                },
                actions=[
                    {
                        "type": "movement",
                        "params": {
                            "close_distance": True
                        }
                    },
                    {
                        "type": "combat",
                        "params": {
                            "style": "aggressive"
                        }
                    }
                ],
                cooldown=1.0
            )
        ]

    def evaluate_behaviors(self, game_state):
        """Évalue et sélectionne le comportement le plus approprié"""
        if not self._validate_game_state(game_state):
            self.logger.warning("État de jeu invalide reçu")
            return None

        current_time = time.time()
        valid_behaviors = []

        for behavior in self.behaviors:
            # Vérification du cooldown
            if behavior.name in self.last_behavior_time:
                if current_time - self.last_behavior_time[behavior.name] < behavior.cooldown:
                    continue

            # Vérification des conditions
            if self._check_conditions(behavior, game_state):
                priority = self._adjust_priority(behavior, game_state)
                valid_behaviors.append((behavior, priority))

        if not valid_behaviors:
            return None

        # Sélection du comportement avec la plus haute priorité ajustée
        selected_behavior, adjusted_priority = max(valid_behaviors, key=lambda x: x[1])
        selected_behavior.priority = adjusted_priority  
        
        # Met à jour l'historique et les cooldowns
        self._update_history(selected_behavior)
        self.last_behavior_time[selected_behavior.name] = current_time
        self.current_state = selected_behavior.state

        return selected_behavior

    def _check_conditions(self, behavior, game_state):
        """Vérifie si les conditions du comportement sont remplies"""
        for condition, value in behavior.conditions.items():
            if condition == 'health_threshold':
                current_health = game_state.get('health', 100) / 100
                if behavior.state == BehaviorState.HEALING:
                    # Pour la guérison, la santé doit être inférieure au seuil
                    if current_health > value:
                        return False
                else:
                    # Pour le combat, la santé doit être supérieure au seuil minimum
                    if current_health < 0.3:  # Seuil de santé critique
                        return False
            elif condition == 'in_combat':
                if game_state.get('in_combat', False) != value:
                    return False
            elif condition == 'has_medkit':
                has_medkit = any(item.get('type') == 'medkit' 
                               for item in game_state.get('inventory', []))
                if has_medkit != value:
                    return False
        return True

    def _adjust_priority(self, behavior, game_state):
        """Ajuste la priorité du comportement en fonction de l'état du jeu"""
        priority = behavior.priority
        
        # Ajustements basés sur la santé
        health_ratio = game_state.get('health', 100) / 100
        if behavior.state == BehaviorState.HEALING:
            priority *= (2.0 - health_ratio)  # Priorité plus élevée quand la santé est basse
            if health_ratio < 0.3:  # Seuil critique de santé
                priority *= 2.0
        
        # Ajustements basés sur le combat
        if behavior.state == BehaviorState.COMBAT:
            if game_state.get('in_combat', False):
                priority *= 1.5  # Augmentation plus importante en combat
                if health_ratio > 0.7:  # Santé suffisante pour le combat
                    priority *= 1.3
            
            # Ajustement basé sur le nombre d'ennemis
            nearby_enemies = game_state.get('nearby_enemies', [])
            if nearby_enemies:
                threat_level = sum(enemy.get('threat_level', 0) for enemy in nearby_enemies)
                priority *= (1 + threat_level * 0.3)
        
        # Ajustements basés sur l'état émotionnel
        emotional_state = game_state.get('emotional_state', {})
        if behavior.state == BehaviorState.HEALING:
            priority *= (1 + emotional_state.get('fear', 0))
        elif behavior.state == BehaviorState.COMBAT:
            priority *= (1 + emotional_state.get('anger', 0))
            priority *= (1 - emotional_state.get('fear', 0) * 0.3)
        
        return min(1.0, max(0.1, priority))

    def _update_history(self, behavior):
        """Met à jour l'historique des comportements"""
        self.state_history.append(behavior.state)
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)

    def get_current_state(self) -> BehaviorState:
        """Retourne l'état actuel du système de comportement"""
        return self.current_state

    def reset_cooldowns(self):
        """Réinitialise tous les cooldowns"""
        self.last_behavior_time.clear()

    def _validate_game_state(self, game_state: Dict[str, Any]) -> bool:
        """Valide l'état du jeu"""
        required_fields = ['health', 'in_combat', 'inventory']
        return all(field in game_state for field in required_fields)

    def update_emotional_state(self, game_state: Dict[str, Any]):
        """Met à jour l'état émotionnel basé sur la situation"""
        # Stress
        stress = 0.0
        stress += (1.0 - game_state.get('health', 100) / 100) * 0.3  
        
        # Impact des ennemis
        nearby_enemies = game_state.get('nearby_enemies', [])
        if nearby_enemies:
            stress += len(nearby_enemies) * 0.2
            # Augmente le stress basé sur le niveau de menace
            threat_level = sum(enemy.get('threat_level', 0) for enemy in nearby_enemies)
            stress += threat_level * 0.3
        
        # Impact de la radiation
        if 'radiation' in game_state:
            stress += (game_state['radiation'] / 100) * 0.2
        
        self.emotional_state['stress'] = min(1.0, max(0.0, stress))

        # Peur
        fear = self.emotional_state['fear'] * 0.9  
        fear += stress * 0.3  
        if nearby_enemies:
            fear += max(enemy.get('threat_level', 0) for enemy in nearby_enemies) * 0.4
        
        # Colère
        anger = self.emotional_state['anger'] * 0.9  
        if game_state.get('in_combat', False):
            anger += 0.3  
        if nearby_enemies:
            anger += len(nearby_enemies) * 0.1
        
        # Confiance
        confidence = self.emotional_state['confidence'] * 0.95  
        confidence += (game_state.get('health', 100) / 100) * 0.2  
        confidence -= fear * 0.3  
        
        self.emotional_state['fear'] = min(1.0, max(0.0, fear))
        self.emotional_state['anger'] = min(1.0, max(0.0, anger))
        self.emotional_state['confidence'] = min(1.0, max(0.0, confidence))

    def get_emotional_state(self) -> Dict[str, float]:
        """Retourne une copie de l'état émotionnel actuel"""
        return self.emotional_state.copy()

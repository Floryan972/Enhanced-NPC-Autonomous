"""
Gestionnaire de comportements pour ENA
"""
from typing import Dict, Any, List, Optional
from ..utils.logger import Logger
from ..utils.config import Config

class BehaviorManager:
    def __init__(self, config: Config):
        self.logger = Logger("BehaviorManager")
        self.config = config
        self.behaviors: Dict[str, Dict[str, Any]] = {}
        self._load_default_behaviors()
        
    def _load_default_behaviors(self):
        """Charge les comportements par défaut"""
        default_behaviors = {
            "idle": {
                "priority": 1.0,
                "conditions": [],
                "actions": ["stand", "look_around"]
            },
            "wander": {
                "priority": 0.8,
                "conditions": ["no_target"],
                "actions": ["walk_random"]
            },
            "interact": {
                "priority": 1.2,
                "conditions": ["near_target"],
                "actions": ["face_target", "talk"]
            },
            "combat": {
                "priority": 1.5,
                "conditions": ["hostile_target"],
                "actions": ["equip_weapon", "attack"]
            },
            "flee": {
                "priority": 2.0,
                "conditions": ["low_health"],
                "actions": ["run_from_target"]
            }
        }
        
        self.behaviors.update(default_behaviors)
        self.logger.info("Comportements par défaut chargés")
        
    def add_behavior(self, name: str, behavior: Dict[str, Any]) -> None:
        """Ajoute un nouveau comportement"""
        try:
            if name in self.behaviors:
                self.logger.warning(f"Le comportement {name} existe déjà et sera écrasé")
            self.behaviors[name] = behavior
            self.logger.info(f"Comportement ajouté: {name}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout du comportement: {str(e)}")
            
    def get_behavior(self, name: str) -> Optional[Dict[str, Any]]:
        """Récupère un comportement"""
        return self.behaviors.get(name)
        
    def remove_behavior(self, name: str) -> None:
        """Supprime un comportement"""
        if name in self.behaviors:
            del self.behaviors[name]
            self.logger.info(f"Comportement supprimé: {name}")
            
    def get_all_behaviors(self) -> List[str]:
        """Récupère la liste des comportements disponibles"""
        return list(self.behaviors.keys())
        
    def evaluate_behavior(self, npc_state: Dict[str, Any], behavior_name: str) -> float:
        """Évalue la priorité d'un comportement pour un PNJ"""
        try:
            behavior = self.behaviors.get(behavior_name)
            if not behavior:
                return 0.0
                
            # Vérifier les conditions
            for condition in behavior.get("conditions", []):
                if not self._check_condition(npc_state, condition):
                    return 0.0
                    
            # Calculer la priorité finale
            base_priority = behavior.get("priority", 1.0)
            return self._calculate_priority(npc_state, base_priority)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation du comportement: {str(e)}")
            return 0.0
            
    def _check_condition(self, npc_state: Dict[str, Any], condition: str) -> bool:
        """Vérifie une condition pour un PNJ"""
        # TODO: Implémenter la vérification des conditions
        return True
        
    def _calculate_priority(self, npc_state: Dict[str, Any], base_priority: float) -> float:
        """Calcule la priorité finale d'un comportement"""
        # TODO: Implémenter le calcul de priorité
        return base_priority

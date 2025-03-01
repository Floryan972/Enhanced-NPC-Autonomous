"""
Gestionnaire de quêtes pour ENA
"""
from typing import Dict, Any, List, Optional
from ..utils.logger import Logger
from ..utils.config import Config

class Quest:
    def __init__(self, quest_id: str, data: Dict[str, Any]):
        self.id = quest_id
        self.title = data.get("title", "")
        self.description = data.get("description", "")
        self.objectives = data.get("objectives", [])
        self.rewards = data.get("rewards", {})
        self.status = "inactive"
        self.progress = {}

class QuestManager:
    def __init__(self, config: Config):
        self.logger = Logger("QuestManager")
        self.config = config
        self.quests: Dict[str, Quest] = {}
        self.active_quests: Dict[str, Quest] = {}
        
    def add_quest(self, quest_id: str, quest_data: Dict[str, Any]) -> Optional[Quest]:
        """Ajoute une nouvelle quête"""
        try:
            if quest_id in self.quests:
                self.logger.warning(f"La quête {quest_id} existe déjà et sera écrasée")
            
            quest = Quest(quest_id, quest_data)
            self.quests[quest_id] = quest
            self.logger.info(f"Quête ajoutée: {quest_id}")
            return quest
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout de la quête: {str(e)}")
            return None
            
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Récupère une quête"""
        return self.quests.get(quest_id)
        
    def activate_quest(self, quest_id: str) -> bool:
        """Active une quête"""
        try:
            quest = self.quests.get(quest_id)
            if not quest:
                self.logger.error(f"Quête non trouvée: {quest_id}")
                return False
                
            if quest.status != "inactive":
                self.logger.warning(f"La quête {quest_id} est déjà active")
                return False
                
            quest.status = "active"
            self.active_quests[quest_id] = quest
            self.logger.info(f"Quête activée: {quest_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'activation de la quête: {str(e)}")
            return False
            
    def update_quest_progress(self, quest_id: str, objective_id: str, progress: Any) -> bool:
        """Met à jour la progression d'une quête"""
        try:
            quest = self.active_quests.get(quest_id)
            if not quest:
                self.logger.error(f"Quête active non trouvée: {quest_id}")
                return False
                
            quest.progress[objective_id] = progress
            self.logger.debug(f"Progression mise à jour pour la quête {quest_id}: {objective_id}")
            
            # Vérifier si la quête est terminée
            if self._check_quest_completion(quest):
                quest.status = "completed"
                del self.active_quests[quest_id]
                self.logger.info(f"Quête terminée: {quest_id}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de la progression: {str(e)}")
            return False
            
    def get_active_quests(self) -> List[Quest]:
        """Récupère la liste des quêtes actives"""
        return list(self.active_quests.values())
        
    def _check_quest_completion(self, quest: Quest) -> bool:
        """Vérifie si une quête est terminée"""
        try:
            for objective in quest.objectives:
                objective_id = objective.get("id")
                required_progress = objective.get("required_progress")
                current_progress = quest.progress.get(objective_id, 0)
                
                if current_progress < required_progress:
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification de la progression: {str(e)}")
            return False

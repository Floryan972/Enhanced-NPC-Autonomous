"""
Gestionnaire de factions pour ENA
"""
from typing import Dict, Any, List, Optional, Tuple
from ..utils.logger import Logger
from ..utils.config import Config

class Faction:
    def __init__(self, faction_id: str, data: Dict[str, Any]):
        self.id = faction_id
        self.name = data.get("name", "")
        self.description = data.get("description", "")
        self.relationships: Dict[str, float] = data.get("relationships", {})
        self.members: List[str] = []

class FactionManager:
    def __init__(self, config: Config):
        self.logger = Logger("FactionManager")
        self.config = config
        self.factions: Dict[str, Faction] = {}
        
    def create_faction(self, faction_id: str, faction_data: Dict[str, Any]) -> Optional[Faction]:
        """Crée une nouvelle faction"""
        try:
            if faction_id in self.factions:
                self.logger.warning(f"La faction {faction_id} existe déjà et sera écrasée")
            
            faction = Faction(faction_id, faction_data)
            self.factions[faction_id] = faction
            self.logger.info(f"Faction créée: {faction_id}")
            return faction
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la création de la faction: {str(e)}")
            return None
            
    def get_faction(self, faction_id: str) -> Optional[Faction]:
        """Récupère une faction"""
        return self.factions.get(faction_id)
        
    def add_member(self, faction_id: str, member_id: str) -> bool:
        """Ajoute un membre à une faction"""
        try:
            faction = self.factions.get(faction_id)
            if not faction:
                self.logger.error(f"Faction non trouvée: {faction_id}")
                return False
                
            if member_id in faction.members:
                self.logger.warning(f"Le membre {member_id} est déjà dans la faction {faction_id}")
                return False
                
            faction.members.append(member_id)
            self.logger.info(f"Membre {member_id} ajouté à la faction {faction_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout du membre: {str(e)}")
            return False
            
    def remove_member(self, faction_id: str, member_id: str) -> bool:
        """Retire un membre d'une faction"""
        try:
            faction = self.factions.get(faction_id)
            if not faction:
                self.logger.error(f"Faction non trouvée: {faction_id}")
                return False
                
            if member_id not in faction.members:
                self.logger.warning(f"Le membre {member_id} n'est pas dans la faction {faction_id}")
                return False
                
            faction.members.remove(member_id)
            self.logger.info(f"Membre {member_id} retiré de la faction {faction_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du retrait du membre: {str(e)}")
            return False
            
    def set_relationship(self, faction_id: str, target_faction_id: str, value: float) -> bool:
        """Définit la relation entre deux factions"""
        try:
            faction = self.factions.get(faction_id)
            target_faction = self.factions.get(target_faction_id)
            
            if not faction or not target_faction:
                self.logger.error("Faction(s) non trouvée(s)")
                return False
                
            faction.relationships[target_faction_id] = value
            target_faction.relationships[faction_id] = value
            self.logger.info(f"Relation définie entre {faction_id} et {target_faction_id}: {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la définition de la relation: {str(e)}")
            return False
            
    def get_relationship(self, faction_id: str, target_faction_id: str) -> float:
        """Récupère la relation entre deux factions"""
        try:
            faction = self.factions.get(faction_id)
            if not faction:
                return 0.0
            return faction.relationships.get(target_faction_id, 0.0)
        except Exception:
            return 0.0
            
    def get_faction_members(self, faction_id: str) -> List[str]:
        """Récupère la liste des membres d'une faction"""
        faction = self.factions.get(faction_id)
        return faction.members if faction else []

"""
Gestionnaire de données pour ENA
"""
from typing import Dict, Any, Optional
from .logger import Logger

class DataManager:
    def __init__(self):
        self.logger = Logger("DataManager")
        self.data = {}
        
    def save(self, key: str, value: Any) -> None:
        """Sauvegarde une donnée"""
        try:
            self.data[key] = value
            self.logger.debug(f"Donnée sauvegardée: {key}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
            
    def load(self, key: str, default: Any = None) -> Any:
        """Charge une donnée"""
        try:
            return self.data.get(key, default)
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement: {str(e)}")
            return default
            
    def delete(self, key: str) -> None:
        """Supprime une donnée"""
        try:
            if key in self.data:
                del self.data[key]
                self.logger.debug(f"Donnée supprimée: {key}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression: {str(e)}")
            
    def clear(self) -> None:
        """Efface toutes les données"""
        try:
            self.data.clear()
            self.logger.debug("Toutes les données ont été effacées")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'effacement: {str(e)}")
            
    def exists(self, key: str) -> bool:
        """Vérifie si une donnée existe"""
        return key in self.data

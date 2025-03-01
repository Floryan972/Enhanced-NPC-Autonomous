"""
Gestionnaire de ressources pour ENA
"""
from typing import Dict, Any, Optional
from .logger import Logger
from .path_manager import PathManager

class ResourceManager:
    def __init__(self):
        self.logger = Logger("ResourceManager")
        self.path_manager = PathManager()
        self.resources: Dict[str, Any] = {}
        
    def load_resource(self, resource_type: str, resource_path: str) -> Optional[Any]:
        """Charge une ressource"""
        try:
            abs_path = self.path_manager.get_absolute_path(resource_path)
            
            if not self.path_manager.is_file(abs_path):
                self.logger.error(f"Ressource non trouvée: {abs_path}")
                return None
                
            # TODO: Implémenter le chargement spécifique selon le type de ressource
            resource = None
            
            if resource:
                self.resources[resource_path] = resource
                self.logger.info(f"Ressource chargée: {resource_path}")
                return resource
            else:
                self.logger.error(f"Impossible de charger la ressource: {resource_path}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la ressource: {str(e)}")
            return None
            
    def get_resource(self, resource_path: str) -> Optional[Any]:
        """Récupère une ressource déjà chargée"""
        return self.resources.get(resource_path)
        
    def unload_resource(self, resource_path: str) -> None:
        """Décharge une ressource"""
        if resource_path in self.resources:
            del self.resources[resource_path]
            self.logger.info(f"Ressource déchargée: {resource_path}")
            
    def clear_resources(self) -> None:
        """Décharge toutes les ressources"""
        self.resources.clear()
        self.logger.info("Toutes les ressources ont été déchargées")

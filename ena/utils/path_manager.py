"""
Gestionnaire de chemins pour ENA
"""
import os
from typing import Optional
from .logger import Logger

class PathManager:
    def __init__(self, base_path: Optional[str] = None):
        self.logger = Logger("PathManager")
        self.base_path = base_path or os.getcwd()
        
    def get_absolute_path(self, relative_path: str) -> str:
        """Convertit un chemin relatif en chemin absolu"""
        try:
            if os.path.isabs(relative_path):
                return relative_path
            return os.path.abspath(os.path.join(self.base_path, relative_path))
        except Exception as e:
            self.logger.error(f"Erreur lors de la conversion du chemin: {str(e)}")
            return relative_path
            
    def get_relative_path(self, absolute_path: str) -> str:
        """Convertit un chemin absolu en chemin relatif"""
        try:
            return os.path.relpath(absolute_path, self.base_path)
        except Exception as e:
            self.logger.error(f"Erreur lors de la conversion du chemin: {str(e)}")
            return absolute_path
            
    def ensure_directory(self, path: str) -> bool:
        """S'assure qu'un répertoire existe"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la création du répertoire: {str(e)}")
            return False
            
    def is_file(self, path: str) -> bool:
        """Vérifie si le chemin pointe vers un fichier"""
        return os.path.isfile(path)
        
    def is_directory(self, path: str) -> bool:
        """Vérifie si le chemin pointe vers un répertoire"""
        return os.path.isdir(path)

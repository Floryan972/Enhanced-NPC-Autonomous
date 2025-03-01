import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

class Logger:
    """Gestionnaire de journalisation pour le système ENA."""
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        self.name = name
        self.logger = logging.getLogger(name)
        
        if not self.logger.handlers:
            self._setup_logger(log_file)
            
    def _setup_logger(self, log_file: Optional[str] = None):
        """Configure le logger."""
        # Configuration par défaut
        self.logger.setLevel(logging.INFO)
        
        # Format du message
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler pour la console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Handler pour le fichier si spécifié
        if log_file:
            try:
                # Création du dossier si nécessaire
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                
                # Configuration du handler de fichier
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=10*1024*1024,  # 10 MB
                    backupCount=5
                )
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
                
            except Exception as e:
                self.error(f"Impossible de configurer le fichier de log: {str(e)}")
                
    def debug(self, message: str):
        """Log un message de niveau DEBUG."""
        self.logger.debug(message)
        
    def info(self, message: str):
        """Log un message de niveau INFO."""
        self.logger.info(message)
        
    def warning(self, message: str):
        """Log un message de niveau WARNING."""
        self.logger.warning(message)
        
    def error(self, message: str):
        """Log un message de niveau ERROR."""
        self.logger.error(message)
        
    def critical(self, message: str):
        """Log un message de niveau CRITICAL."""
        self.logger.critical(message)
        
    def set_level(self, level: str):
        """Définit le niveau de log."""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        
        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
        else:
            self.warning(f"Niveau de log invalide: {level}")
            
    def add_file_handler(self, log_file: str):
        """Ajoute un handler de fichier."""
        try:
            # Création du dossier si nécessaire
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            # Configuration du handler
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10 MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            
            # Ajout du handler
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            self.error(f"Impossible d'ajouter le handler de fichier: {str(e)}")
            
    def remove_file_handlers(self):
        """Supprime tous les handlers de fichier."""
        for handler in self.logger.handlers[:]:
            if isinstance(handler, RotatingFileHandler):
                self.logger.removeHandler(handler)
                
    def clear_handlers(self):
        """Supprime tous les handlers."""
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

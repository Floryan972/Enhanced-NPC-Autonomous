"""
Chargeur de plugin pour Enhanced NPC Autonomous
"""
import sys
from pathlib import Path
import logging
from datetime import datetime

# Configuration des chemins
PLUGIN_ROOT = Path(__file__).parent
LOGS_DIR = PLUGIN_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configuration du logging
def setup_logging():
    # Crée un logger pour le plugin
    logger = logging.getLogger("EnhancedNPCAutonomous")
    logger.setLevel(logging.DEBUG)
    
    # Format du timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Handler pour le fichier de log général
    general_log = LOGS_DIR / f"plugin_{timestamp}.log"
    file_handler = logging.FileHandler(general_log, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Format des logs
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Ajout des handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialisation du plugin
def initialize_plugin():
    logger = setup_logging()
    logger.info("=== Initialisation du plugin Enhanced NPC Autonomous ===")
    
    try:
        # Ajout du chemin du plugin au PYTHONPATH
        if str(PLUGIN_ROOT) not in sys.path:
            sys.path.append(str(PLUGIN_ROOT))
            logger.info(f"Chemin du plugin ajouté: {PLUGIN_ROOT}")
        
        # Import des modules nécessaires
        from player_ai.unified_player_system import UnifiedPlayerController
        from player_ai.ai_logger import AILogger
        
        # Création des instances
        controller = UnifiedPlayerController()
        ai_logger = AILogger()
        
        logger.info("Plugin chargé avec succès")
        logger.info("Contrôleur IA initialisé")
        logger.info("Système de logging configuré")
        
        return controller, ai_logger
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du plugin: {e}")
        raise

if __name__ == "__main__":
    initialize_plugin()

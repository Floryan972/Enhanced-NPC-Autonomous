"""
Point d'entrée principal d'ENA
"""
import argparse
import sys
import time
from pathlib import Path
from .utils.logger import Logger
from .utils.config import Config
from .core import (
    AIManager,
    BehaviorManager,
    EventManager,
    WorldManager,
    QuestManager,
    FactionManager
)

def main():
    # Configuration du parser d'arguments
    parser = argparse.ArgumentParser(description="Enhanced NPC Autonomous (ENA) System")
    parser.add_argument("--config", type=str, help="Chemin vers le fichier de configuration")
    args = parser.parse_args()
    
    # Initialisation du logger
    logger = Logger("ENA")
    logger.info("Démarrage d'ENA...")
    
    try:
        # Chargement de la configuration
        config_path = args.config if args.config else "config/ena_config.json"
        if not Path(config_path).exists():
            logger.error(f"Fichier de configuration non trouvé: {config_path}")
            sys.exit(1)
            
        config = Config(config_path)
        
        # Initialisation des gestionnaires
        event_manager = EventManager()
        world_manager = WorldManager(config)
        quest_manager = QuestManager(config)
        faction_manager = FactionManager(config)
        behavior_manager = BehaviorManager(config)
        ai_manager = AIManager(config)
        
        # Configuration des événements
        event_manager.subscribe("npc_spawn", world_manager.handle_npc_spawn)
        event_manager.subscribe("npc_action", ai_manager.handle_npc_action)
        
        logger.info("ENA initialisé avec succès")
        
        # Variables pour le timing
        last_time = time.time()
        
        # Boucle principale
        while True:
            try:
                # Calcul du delta time
                current_time = time.time()
                delta_time = current_time - last_time
                last_time = current_time
                
                # Mise à jour des gestionnaires
                world_manager.update(delta_time)
                ai_manager.update(delta_time)
                
            except KeyboardInterrupt:
                logger.info("Arrêt d'ENA...")
                break
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle principale: {str(e)}")
                continue
                
            # Petite pause pour éviter de surcharger le CPU
            time.sleep(0.01)
                
    except Exception as e:
        logger.error(f"Erreur fatale: {str(e)}")
        sys.exit(1)
        
if __name__ == "__main__":
    main()

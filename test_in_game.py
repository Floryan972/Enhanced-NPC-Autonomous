"""
Script de test en jeu pour le plugin Enhanced NPC Autonomous
"""
import time
import logging
import sys
import os
from pathlib import Path

# Configuration du logging immédiatement
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()  # Log vers la console d'abord
    ]
)
logger = logging.getLogger(__name__)

# Vérification des chemins
plugin_path = Path("D:/ELECTRONIC'S ARTS/STALKER 2 Heart of Chornobyl/bin/plugins/enhanced_npc_autonomous")
logger.debug(f"Chemin du plugin: {plugin_path}")
logger.debug(f"Le chemin existe: {plugin_path.exists()}")

# Ajout du chemin du plugin aux chemins Python
sys.path.append(str(plugin_path))
logger.debug(f"Python path: {sys.path}")

# Vérification des fichiers nécessaires
logger.debug("Vérification des fichiers nécessaires:")
files_to_check = [
    plugin_path / "player_ai" / "unified_player_system.py",
    plugin_path / "player_ai" / "ai_logger.py",
    plugin_path / "config" / "config.ini"
]
for file in files_to_check:
    logger.debug(f"Fichier {file}: {'existe' if file.exists() else 'MANQUANT'}")

try:
    from player_ai.ai_logger import AILogger
    logger.debug("Import AILogger réussi")
except Exception as e:
    logger.error(f"Erreur lors de l'import de AILogger: {e}")

try:
    from player_ai.unified_player_system import UnifiedPlayerController, PlayerAutonomousSystem
    logger.debug("Import UnifiedPlayerController et PlayerAutonomousSystem réussi")
except Exception as e:
    logger.error(f"Erreur lors de l'import: {e}")

def setup_test_logger():
    """Configure le système de logging pour les tests"""
    try:
        # Création du dossier de logs s'il n'existe pas
        log_dir = plugin_path / "logs"
        log_dir.mkdir(exist_ok=True)
        logger.debug(f"Dossier de logs créé: {log_dir}")

        # Ajout du handler de fichier
        file_handler = logging.FileHandler(log_dir / 'test_debug.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logging.getLogger().addHandler(file_handler)
        
        # Configuration du logger AI
        ai_logger = AILogger()
        logger.debug("Logger AI configuré")
        
        return ai_logger
    except Exception as e:
        logger.error(f"Erreur lors de la configuration du logger: {e}")
        raise

def test_npc_behavior(ai_logger):
    """Test le comportement d'un PNJ dans différentes situations"""
    try:
        logger.debug("Initialisation du système de contrôle unifié")
        controller = UnifiedPlayerController()
        ai_system = PlayerAutonomousSystem()
        
        # État initial
        initial_state = {
            "player": {
                "npc_id": "test_stalker_1",
                "position": {"x": 0, "y": 0, "z": 0},
                "health": 100,
                "stamina": 100,
                "inventory": {
                    "weapons": ["ak74", "pm"],
                    "items": ["medkit", "bandage", "bread"]
                }
            },
            "environment": {
                "time_of_day": "day",
                "weather": "clear",
                "radiation_level": 0.1
            },
            "nearby_entities": []
        }
        
        # État avec ennemi
        combat_state = {
            "player": initial_state["player"].copy(),
            "environment": initial_state["environment"].copy(),
            "nearby_entities": [
                {
                    "id": "enemy_bandit_1",
                    "type": "enemy",
                    "position": {"x": 10, "y": 0, "z": 0},
                    "health": 100,
                    "threat_level": "high"
                }
            ]
        }
        
        logger.info("=== Début du test de comportement PNJ ===")
        
        # Test 1: Activation du mode IA
        logger.info("Test 1: Activation du mode IA")
        try:
            # Log du changement d'état initial
            ai_logger.log_state_change(
                old_state={"mode": "manual"},
                new_state={"mode": "ai_controlled"},
                trigger="toggle_ai_mode"
            )
            
            controller.toggle_ai_mode()
            controller.update(initial_state, 0.1)
            
            # Log de la décision
            ai_logger.log_decision(
                context=initial_state,
                decision_type="mode_change",
                decision_details={
                    "action": "activate_ai",
                    "reason": "Test activation"
                },
                confidence=1.0
            )
            
            logger.info("IA activée - Prise de contrôle du personnage")
        except Exception as e:
            logger.error(f"Erreur lors de l'activation du mode IA: {e}")
        time.sleep(1)
        
        # Test 2: Mise à jour du système autonome
        logger.info("Test 2: Mise à jour du système autonome")
        try:
            # Log du changement d'état pour le combat
            ai_logger.log_state_change(
                old_state=initial_state,
                new_state=combat_state,
                trigger="enemy_detected"
            )
            
            ai_system.update(combat_state)
            
            # Log de la décision de combat
            ai_logger.log_combat(
                threat=combat_state["nearby_entities"][0],
                action={
                    "type": "engage",
                    "weapon": "ak74",
                    "distance": 10.0,
                    "cover": True
                },
                player_state=combat_state["player"]
            )
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour: {e}")
        time.sleep(1)
        
        # Vérification finale des logs
        logger.debug("Vérification des fichiers de log:")
        log_files = list((plugin_path / "logs").glob("*.log"))
        for log_file in log_files:
            logger.debug(f"Fichier log trouvé: {log_file}")
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    last_lines = f.readlines()[-5:]  # Dernières 5 lignes
                    logger.debug(f"Dernières lignes de {log_file.name}:")
                    for line in last_lines:
                        logger.debug(line.strip())
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du log {log_file}: {e}")
        
        return combat_state
    except Exception as e:
        logger.error(f"Erreur générale pendant les tests: {e}")
        raise

def main():
    try:
        logger.info("Démarrage des tests en jeu")
        ai_logger = setup_test_logger()
        final_state = test_npc_behavior(ai_logger)
        logger.info(f"Tests terminés. État final: {final_state}")
    except Exception as e:
        logger.error(f"Erreur critique pendant les tests: {str(e)}")
        raise

if __name__ == "__main__":
    main()

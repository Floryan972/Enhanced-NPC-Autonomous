"""
Script pour activer et contrôler l'IA du joueur
"""
import sys
import time
from pathlib import Path
import logging
import json
from typing import Dict, Any
from datetime import datetime
import subprocess
import ctypes
import win32com.shell.shell as shell
from win32com.shell import shellcon

# Ajout du chemin du plugin
plugin_path = Path("D:/ELECTRONIC'S ARTS/STALKER 2 Heart of Chornobyl/bin/plugins/enhanced_npc_autonomous")
sys.path.append(str(plugin_path))

try:
    from plugin_loader import initialize_plugin
    logger = logging.getLogger("EnhancedNPCAutonomous")
except ImportError as e:
    print(f"Erreur d'import du plugin_loader: {e}")
    sys.exit(1)

class AIController:
    def __init__(self):
        try:
            # Initialisation du plugin et récupération des instances
            self.controller, self.ai_logger = initialize_plugin()
            self.running = True
            self.last_update = time.time()
            self.game_process = None
            
            # Chemins des exécutables
            self.game_paths = {
                "test": Path("D:/ELECTRONIC'S ARTS/STALKER 2 Heart of Chornobyl/Stalker2/Binaries/Win64/Stalker2-Win64-Test.exe"),
                "shipping": Path("D:/ELECTRONIC'S ARTS/STALKER 2 Heart of Chornobyl/Stalker2/Binaries/Win64/Stalker2-Win64-Shipping.exe"),
                "main": Path("D:/ELECTRONIC'S ARTS/STALKER 2 Heart of Chornobyl/Stalker2.exe")
            }
            
            # État de test du jeu
            self.game_state = {
                "player": {
                    "npc_id": "player_1",
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
            
            logger.info("=== Initialisation du Contrôleur d'IA ===")
            logger.info("État initial du joueur:")
            logger.info(json.dumps(self.game_state["player"], indent=2))
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation: {e}")
            raise

    def is_admin(self):
        """Vérifie si le script a les droits administrateur"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_as_admin(self, cmd):
        """Lance une commande en tant qu'administrateur"""
        try:
            params = f'"{cmd}"'
            return shell.ShellExecuteEx(
                nShow=shellcon.SW_SHOW,
                fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                lpVerb='runas',  # Demande les privilèges admin
                lpFile=cmd,
                lpParameters=''
            )
        except Exception as e:
            logger.error(f"Erreur lors du lancement en admin: {e}")
            return None

    def start_game(self, version="test"):
        """Lance le jeu avec la version spécifiée"""
        if not self.game_process:
            try:
                game_exe = self.game_paths.get(version)
                if not game_exe.exists():
                    logger.error(f"Exécutable non trouvé: {game_exe}")
                    print(f"\nErreur: Exécutable non trouvé: {game_exe}")
                    return

                logger.info(f"Lancement de STALKER 2 ({version})...")
                print(f"\nLancement de STALKER 2 ({version})...")
                
                # Lance en tant qu'administrateur
                process_info = self.run_as_admin(str(game_exe))
                if process_info:
                    self.game_process = process_info['hProcess']
                    logger.info("Jeu lancé avec succès")
                    print("Jeu lancé avec succès")
                else:
                    logger.error("Échec du lancement du jeu")
                    print("\nÉchec du lancement du jeu")

            except Exception as e:
                logger.error(f"Erreur lors du lancement du jeu: {e}")
                print(f"\nErreur lors du lancement du jeu: {e}")
    
    def print_status(self):
        """Affiche le statut actuel de l'IA"""
        state = self.controller.get_current_state()
        status = self.controller.get_ai_status()
        
        status_info = {
            "mode": state["mode"],
            "ai_active": state["ai_active"],
            "status": status
        }
        
        logger.info("=== Statut de l'IA ===")
        logger.info(json.dumps(status_info, indent=2))
        
        print("\n=== Statut de l'IA ===")
        print(f"Mode: {state['mode']}")
        print(f"IA active: {'Oui' if state['ai_active'] else 'Non'}")
        
        if status:
            print(f"\nObjectif actuel: {status['current_objective']}")
            print(f"Santé: {status['health']}")
            print(f"Menaces à proximité: {status['nearby_threats']}")
            print("\nProfil comportemental:")
            for trait, value in status['behavioral_profile'].items():
                print(f"- {trait}: {value:.2f}")
    
    def add_enemy(self):
        """Ajoute un ennemi proche"""
        enemy = {
            "id": "enemy_bandit_1",
            "type": "enemy",
            "position": {"x": 10, "y": 0, "z": 0},
            "health": 100,
            "threat_level": "high"
        }
        self.game_state["nearby_entities"].append(enemy)
        
        logger.info("=== Ennemi Détecté ===")
        logger.info(json.dumps(enemy, indent=2))
        
        # Log du changement d'état
        self.ai_logger.log_state_change(
            old_state={"nearby_entities": []},
            new_state={"nearby_entities": [enemy]},
            trigger="enemy_detected"
        )
        
        print("\nEnnemi détecté à proximité!")
        
    def remove_enemy(self):
        """Retire l'ennemi"""
        old_entities = self.game_state["nearby_entities"]
        self.game_state["nearby_entities"] = []
        
        logger.info("=== Zone Sécurisée ===")
        logger.info("Tous les ennemis ont été éliminés")
        
        # Log du changement d'état
        self.ai_logger.log_state_change(
            old_state={"nearby_entities": old_entities},
            new_state={"nearby_entities": []},
            trigger="area_cleared"
        )
        
        print("\nZone sécurisée - plus d'ennemis")
    
    def damage_player(self):
        """Inflige des dégâts au joueur"""
        old_health = self.game_state["player"]["health"]
        self.game_state["player"]["health"] -= 20
        if self.game_state["player"]["health"] < 0:
            self.game_state["player"]["health"] = 0
            
        logger.info("=== Dégâts Subis ===")
        logger.info(f"Santé: {old_health} -> {self.game_state['player']['health']}")
        
        # Log du changement d'état
        self.ai_logger.log_state_change(
            old_state={"health": old_health},
            new_state={"health": self.game_state["player"]["health"]},
            trigger="damage_taken"
        )
        
        print(f"\nDégâts subis! Santé: {self.game_state['player']['health']}")
    
    def heal_player(self):
        """Soigne le joueur"""
        old_health = self.game_state["player"]["health"]
        self.game_state["player"]["health"] = 100
        
        logger.info("=== Soins ===")
        logger.info(f"Santé: {old_health} -> 100")
        
        # Log du changement d'état
        self.ai_logger.log_state_change(
            old_state={"health": old_health},
            new_state={"health": 100},
            trigger="healing"
        )
        
        print("\nJoueur soigné!")
    
    def print_menu(self):
        """Affiche le menu"""
        print("\n=== Menu de Contrôle ===")
        print("\\  - Activer/Désactiver l'IA")
        print("[  - Afficher le statut")
        print("]  - Ajouter un ennemi")
        print("4  - Retirer l'ennemi")
        print("5  - Infliger des dégâts")
        print("6  - Soigner le joueur")
        print("t  - Lancer le jeu (Version Test)")
        print("s  - Lancer le jeu (Version Shipping)")
        print("m  - Lancer le jeu (Version Principale)")
        print("0  - Quitter")
        
    def update_ai(self):
        """Met à jour l'IA et enregistre ses décisions"""
        current_time = time.time()
        if current_time - self.last_update >= 0.1:  # Update every 100ms
            if self.controller.get_current_state()['ai_active']:
                action = self.controller.update(self.game_state, 0.1)
                
                if action:
                    logger.info("=== Décision de l'IA ===")
                    logger.info(json.dumps(action, indent=2))
                    
                    # Log de la décision
                    self.ai_logger.log_decision(
                        context=self.game_state,
                        decision_type=action.get("type", "unknown"),
                        decision_details=action,
                        confidence=action.get("confidence", 1.0)
                    )
            
            self.last_update = current_time
    
    def run(self):
        """Boucle principale"""
        logger.info("=== Démarrage du Contrôleur d'IA STALKER 2 ===")
        print("=== Contrôleur d'IA STALKER 2 ===")
        
        while self.running:
            self.print_menu()
            choice = input("\nChoix: ").strip()
            
            try:
                if choice == "\\":
                    result = self.controller.toggle_ai_mode()
                    state = self.controller.get_current_state()
                    logger.info(f"=== Changement de Mode ===")
                    logger.info(f"Nouveau mode: {state['mode']}")
                    print(f"\nMode IA: {state['mode']}")
                    
                elif choice == "[":
                    self.print_status()
                    
                elif choice == "]":
                    self.add_enemy()
                    
                elif choice == "4":
                    self.remove_enemy()
                    
                elif choice == "5":
                    self.damage_player()
                    
                elif choice == "6":
                    self.heal_player()
                    
                elif choice == "t":
                    self.start_game("test")
                    
                elif choice == "s":
                    self.start_game("shipping")
                    
                elif choice == "m":
                    self.start_game("main")
                    
                elif choice == "0":
                    logger.info("=== Arrêt du Contrôleur ===")
                    print("\nArrêt du contrôleur...")
                    self.running = False
                    if self.game_process:
                        try:
                            shell.ShellExecuteEx(fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                                               lpVerb='runas',
                                               lpFile='taskkill',
                                               lpParameters=f'/F /PID {self.game_process}')
                        except:
                            pass
                    
                else:
                    print("\nChoix invalide!")
                
                self.update_ai()
                    
            except Exception as e:
                logger.error(f"Erreur: {e}")
                
            time.sleep(0.1)  # Petit délai pour éviter de surcharger le CPU

def main():
    try:
        controller = AIController()
        controller.run()
    except Exception as e:
        logger.error(f"Erreur critique: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())

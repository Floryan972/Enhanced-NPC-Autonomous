"""
Script d'installation pour le plugin Enhanced NPC Autonomous
"""

import os
import shutil
import json
import configparser
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('install.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class PluginInstaller:
    def __init__(self):
        self.plugin_name = "Enhanced NPC Autonomous"
        self.current_dir = Path(__file__).parent
        self.game_dir = self.current_dir.parent
        
        # Création des chemins d'installation
        self.plugin_dir = self.game_dir / "bin" / "plugins" / "enhanced_npc_autonomous"
        self.logs_dir = self.plugin_dir / "logs"
        self.config_dir = self.plugin_dir / "config"
        
        # Chemins du plugin UE4
        self.ue4_plugin_dir = self.game_dir / "Stalker2" / "Plugins" / "EnhancedNPCAutonomous"
        self.ue4_source_dir = self.ue4_plugin_dir / "Source"
        self.ue4_content_dir = self.ue4_plugin_dir / "Content"
        
        # Fichiers source
        self.src_dir = self.current_dir / "src"
        self.tests_dir = self.current_dir / "tests"
        
    def create_directories(self):
        """Crée les répertoires nécessaires"""
        dirs = [
            self.plugin_dir,
            self.logs_dir,
            self.config_dir,
            self.plugin_dir / "player_ai",
            self.ue4_plugin_dir,
            self.ue4_source_dir / "Private",
            self.ue4_source_dir / "Public",
            self.ue4_content_dir / "Python"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Créé le répertoire: {dir_path}")
    
    def copy_source_files(self):
        """Copie les fichiers source"""
        # Copie des fichiers Python du plugin
        python_files = [
            (self.src_dir / "player_ai" / "unified_player_system.py", 
             self.plugin_dir / "player_ai" / "unified_player_system.py"),
            (self.src_dir / "logs" / "ai_logger.py",
             self.plugin_dir / "player_ai" / "ai_logger.py"),
            (self.current_dir / "plugin_loader.py",
             self.plugin_dir / "plugin_loader.py")
        ]
        
        # Copie des fichiers du plugin UE4
        ue4_files = [
            # Fichier de configuration du plugin
            (self.current_dir / "EnhancedNPCAutonomous.uplugin",
             self.ue4_plugin_dir / "EnhancedNPCAutonomous.uplugin"),
            
            # Fichiers source C++
            (self.current_dir / "Source" / "EnhancedNPCAutonomous.Build.cs",
             self.ue4_source_dir / "EnhancedNPCAutonomous.Build.cs"),
            (self.current_dir / "Source" / "Private" / "EnhancedNPCAutonomous.cpp",
             self.ue4_source_dir / "Private" / "EnhancedNPCAutonomous.cpp"),
            (self.current_dir / "Source" / "Public" / "EnhancedNPCAutonomous.h",
             self.ue4_source_dir / "Public" / "EnhancedNPCAutonomous.h"),
             
            # Script Python d'initialisation
            (self.current_dir / "Content" / "Python" / "plugin_init.py",
             self.ue4_content_dir / "Python" / "plugin_init.py")
        ]
        
        # Copie tous les fichiers
        for src, dst in python_files + ue4_files:
            if src.exists():
                shutil.copy2(src, dst)
                logging.info(f"Copié: {src} -> {dst}")
            else:
                logging.warning(f"Fichier source non trouvé: {src}")
    
    def create_config(self):
        """Crée les fichiers de configuration"""
        # Configuration JSON
        config_json = {
            "plugin_name": self.plugin_name,
            "version": "1.0.0",
            "author": "Codeium",
            "description": "Système de contrôle IA avancé pour les PNJ",
            "settings": {
                "ai_enabled": True,
                "log_level": "INFO",
                "max_log_size_mb": 100,
                "max_log_files": 10,
                "archive_days": 7
            },
            "paths": {
                "logs": str(self.logs_dir),
                "player_ai": str(self.plugin_dir / "player_ai"),
                "ue4_plugin": str(self.ue4_plugin_dir)
            }
        }
        
        # Écriture du fichier JSON
        config_json_file = self.config_dir / "config.json"
        with open(config_json_file, 'w', encoding='utf-8') as f:
            json.dump(config_json, f, indent=4)
        logging.info(f"Créé le fichier de configuration JSON: {config_json_file}")
        
        # Configuration INI
        config = configparser.ConfigParser()
        
        # Section Plugin
        config['Plugin'] = {
            'name': self.plugin_name,
            'version': '1.0.0',
            'author': 'Codeium',
            'description': 'Système de contrôle IA avancé pour les PNJ'
        }
        
        # Section UE4
        config['UE4'] = {
            'plugin_dir': str(self.ue4_plugin_dir),
            'content_dir': str(self.ue4_content_dir),
            'source_dir': str(self.ue4_source_dir)
        }
        
        # Section Settings
        config['Settings'] = {
            'ai_enabled': 'true',
            'log_level': 'INFO',
            'max_log_size_mb': '100',
            'max_log_files': '10',
            'archive_days': '7'
        }
        
        # Section Paths
        config['Paths'] = {
            'logs': '${PLUGIN_DIR}/logs',
            'player_ai': '${PLUGIN_DIR}/player_ai'
        }
        
        # Section AI
        config['AI'] = {
            'decision_threshold': '0.7',
            'combat_reaction_time': '0.3',
            'state_update_interval': '1.0',
            'memory_size': '1000'
        }
        
        # Section Combat
        config['Combat'] = {
            'min_distance': '5.0',
            'max_distance': '50.0',
            'cover_threshold': '0.6',
            'healing_threshold': '0.4'
        }
        
        # Section Behavior
        config['Behavior'] = {
            'group_cohesion': '0.8',
            'aggression_factor': '0.6',
            'self_preservation': '0.7',
            'curiosity': '0.5'
        }
        
        # Section Debug
        config['Debug'] = {
            'enable_debug_logging': 'false',
            'print_decisions': 'true',
            'save_state_changes': 'true',
            'performance_monitoring': 'false'
        }
        
        # Section Performance
        config['Performance'] = {
            'max_concurrent_decisions': '100',
            'update_frequency': '60',
            'cache_size': '1024',
            'cleanup_interval': '300'
        }
        
        # Écriture du fichier INI
        config_ini_file = self.config_dir / "config.ini"
        with open(config_ini_file, 'w', encoding='utf-8') as f:
            config.write(f)
        logging.info(f"Créé le fichier de configuration INI: {config_ini_file}")
    
    def create_plugin_info(self):
        """Crée le fichier plugin.info"""
        plugin_info = {
            "name": self.plugin_name,
            "version": "1.0.0",
            "api_version": "1.0",
            "entry_point": "player_ai.unified_player_system",
            "ue4_plugin": {
                "name": "EnhancedNPCAutonomous",
                "enabled": True,
                "loading_phase": "PreDefault"
            },
            "dependencies": ["PythonScriptPlugin"],
            "load_order": 100,
            "author": "Codeium",
            "website": "https://codeium.com",
            "description": "Système de contrôle IA avancé pour les PNJ"
        }
        
        info_file = self.plugin_dir / "plugin.info"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(plugin_info, f, indent=4)
        logging.info(f"Créé le fichier plugin.info: {info_file}")
    
    def install(self):
        """Installe le plugin"""
        try:
            logging.info(f"Début de l'installation de {self.plugin_name}")
            
            # Création des répertoires
            self.create_directories()
            
            # Copie des fichiers
            self.copy_source_files()
            
            # Création des fichiers de configuration
            self.create_config()
            self.create_plugin_info()
            
            logging.info(f"Installation de {self.plugin_name} terminée avec succès")
            print("\nInstallation terminée avec succès!")
            print("\nPour utiliser le plugin :")
            print("1. Lancez le jeu")
            print("2. Utilisez les touches suivantes :")
            print("   - \\ : Activer/désactiver l'IA")
            print("   - [ : Afficher le statut")
            print("   - ] : Ajouter un ennemi")
            print("\nLes logs sont disponibles dans :")
            print(f"{self.logs_dir}")
            
            return True
            
        except Exception as e:
            logging.error(f"Erreur lors de l'installation: {e}")
            print(f"\nErreur lors de l'installation: {e}")
            return False

if __name__ == "__main__":
    installer = PluginInstaller()
    success = installer.install()

"""
Script d'initialisation de l'environnement ENA
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Vérifie la version de Python"""
    if sys.version_info < (3, 9):
        print("ENA nécessite Python 3.9 ou supérieur")
        sys.exit(1)

def create_directories():
    """Crée les répertoires nécessaires"""
    directories = [
        "data/npcs",
        "data/quests",
        "data/factions",
        "data/worlds",
        "models/lmstudio",
        "logs",
        "config/games"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Répertoire créé: {directory}")

def setup_venv():
    """Configure l'environnement virtuel"""
    if not Path("venv").exists():
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("Environnement virtuel créé")
    
    # Activation du venv
    if sys.platform == "win32":
        pip_path = "venv/Scripts/pip"
    else:
        pip_path = "venv/bin/pip"
    
    # Mise à jour de pip
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
    
    # Installation des dépendances
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
    print("Dépendances installées")

def create_default_config():
    """Crée la configuration par défaut"""
    config = {
        "model": {
            "type": "lmstudio",
            "path": "models/lmstudio",
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 2048,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
        },
        "vortex": {
            "enabled": True,
            "host": "localhost",
            "port": 8000
        },
        "logging": {
            "level": "INFO",
            "file": "logs/ena.log"
        },
        "database": {
            "type": "sqlite",
            "path": "data/ena.db"
        },
        "games": {
            "supported": ["stalker2", "cyberpunk2077", "starfield", "rdr2"],
            "default": "stalker2"
        },
        "ai": {
            "update_interval": 0.1,
            "max_npcs": 1000,
            "behavior_weights": {
                "idle": 1.0,
                "wander": 0.8,
                "interact": 1.2,
                "combat": 1.5,
                "flee": 2.0
            }
        },
        "performance": {
            "threading": {
                "enabled": True,
                "max_workers": 4
            },
            "caching": {
                "enabled": True,
                "max_size": 1000
            }
        }
    }
    
    with open("config/ena_config.json", "w") as f:
        json.dump(config, f, indent=4)
    print("Configuration par défaut créée")

def main():
    """Fonction principale"""
    print("Configuration de l'environnement ENA...")
    
    try:
        check_python_version()
        create_directories()
        setup_venv()
        create_default_config()
        
        print("\nConfiguration terminée avec succès!")
        print("\nPour démarrer ENA:")
        print("1. Activez l'environnement virtuel:")
        if sys.platform == "win32":
            print("   .\\venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("2. Lancez ENA:")
        print("   python -m ena")
        
    except Exception as e:
        print(f"\nErreur lors de la configuration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

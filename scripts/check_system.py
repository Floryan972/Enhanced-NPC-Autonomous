"""
Script de verification de l'etat du systeme ENA
"""
import os
import sys
import json
import importlib
import subprocess
from pathlib import Path

def check_dependencies():
    """Verifie les dependances Python"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "numpy",
        "torch",
        "transformers",
        "sqlalchemy",
        "redis",
        "pygame"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def check_directories():
    """Verifie les repertoires requis"""
    required_dirs = [
        "data/npcs",
        "data/quests",
        "data/factions",
        "data/worlds",
        "models/lmstudio",
        "logs",
        "config"
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not Path(directory).exists():
            missing_dirs.append(directory)
    
    return missing_dirs

def check_config():
    """Verifie la configuration"""
    config_path = "config/ena_config.json"
    if not Path(config_path).exists():
        return False, "Fichier de configuration manquant"
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            
        required_keys = ["model", "vortex", "logging", "database", "games", "ai"]
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            return False, f"Cles manquantes dans la configuration: {', '.join(missing_keys)}"
            
        return True, "Configuration valide"
        
    except json.JSONDecodeError:
        return False, "Erreur de syntaxe dans le fichier de configuration"
    except Exception as e:
        return False, f"Erreur lors de la verification de la configuration: {str(e)}"

def check_model():
    """Verifie le modele LM Studio"""
    model_path = "models/lmstudio"
    required_files = ["llama-3.2-3b-instruct-q8_0.gguf", "config.json"]
    
    missing_files = []
    for file in required_files:
        if not Path(f"{model_path}/{file}").exists():
            missing_files.append(file)
    
    return missing_files

def check_python_version():
    """Verifie la version de Python"""
    return sys.version_info >= (3, 9)

def check_disk_space():
    """Verifie l'espace disque"""
    try:
        if sys.platform == "win32":
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p("."), None, None, ctypes.pointer(free_bytes))
            free_gb = free_bytes.value / (1024**3)
            
            return True, f"Espace libre: {free_gb:.1f}GB"
        else:
            total, used, free = os.statvfs(".").f_blocks, os.statvfs(".").f_bfree, os.statvfs(".").f_bavail
            total_gb = (total * os.statvfs(".").f_frsize) / (1024**3)
            free_gb = (free * os.statvfs(".").f_frsize) / (1024**3)
            
            return True, f"Espace total: {total_gb:.1f}GB, Espace libre: {free_gb:.1f}GB"
            
    except Exception as e:
        return False, f"Erreur lors de la verification de l'espace disque: {str(e)}"

def main():
    """Fonction principale"""
    print("Verification du systeme ENA...\n")
    
    # Verification de Python
    print("Python version:", end=" ")
    if check_python_version():
        print("[OK]")
    else:
        print("[ERREUR] Python 3.9 ou superieur requis")
    
    # Verification des dependances
    print("\nDependances Python:", end=" ")
    missing_packages = check_dependencies()
    if not missing_packages:
        print("[OK]")
    else:
        print(f"[ERREUR] Manquantes: {', '.join(missing_packages)}")
    
    # Verification des repertoires
    print("\nRepertoires requis:", end=" ")
    missing_dirs = check_directories()
    if not missing_dirs:
        print("[OK]")
    else:
        print(f"[ERREUR] Manquants: {', '.join(missing_dirs)}")
    
    # Verification de la configuration
    print("\nConfiguration:", end=" ")
    config_ok, config_msg = check_config()
    if config_ok:
        print("[OK]")
    else:
        print(f"[ERREUR] {config_msg}")
    
    # Verification du modele
    print("\nModele LM Studio:", end=" ")
    missing_files = check_model()
    if not missing_files:
        print("[OK]")
    else:
        print(f"[ERREUR] Fichiers manquants: {', '.join(missing_files)}")
    
    # Verification de l'espace disque
    print("\nEspace disque:", end=" ")
    space_ok, space_msg = check_disk_space()
    if space_ok:
        print(f"[OK] {space_msg}")
    else:
        print(f"[ERREUR] {space_msg}")
    
    print("\nVerification terminee!")

if __name__ == "__main__":
    main()

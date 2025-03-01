"""
Script pour démarrer ENA avec Vortex
"""
import os
import sys
import json
import time
import subprocess
from pathlib import Path

def load_config():
    """Charge la configuration"""
    try:
        with open("config/ena_config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration: {str(e)}")
        sys.exit(1)

def check_vortex():
    """Vérifie si Vortex est en cours d'exécution"""
    import psutil
    for proc in psutil.process_iter(['name']):
        if "vortex" in proc.info['name'].lower():
            return True
    return False

def main():
    """Fonction principale"""
    print("Démarrage d'ENA avec Vortex...")
    
    # Charger la configuration
    config = load_config()
    if not config["vortex"]["enabled"]:
        print("Vortex n'est pas activé dans la configuration")
        sys.exit(1)
    
    # Vérifier si Vortex est en cours d'exécution
    if not check_vortex():
        print("Vortex n'est pas en cours d'exécution")
        print("Veuillez démarrer Vortex et réessayer")
        sys.exit(1)
    
    # Démarrer ENA
    try:
        print("\nDémarrage d'ENA...")
        ena_process = subprocess.Popen(
            [sys.executable, "-m", "ena"],
            cwd=os.getcwd()
        )
        
        # Attendre que ENA démarre
        time.sleep(2)
        
        if ena_process.poll() is not None:
            print("Erreur lors du démarrage d'ENA")
            sys.exit(1)
        
        print("\nENA est maintenant connecté à Vortex")
        print(f"Port Vortex: {config['vortex']['port']}")
        print(f"Hôte Vortex: {config['vortex']['host']}")
        print("\nAppuyez sur Ctrl+C pour arrêter")
        
        # Maintenir le processus en vie
        while True:
            if ena_process.poll() is not None:
                print("\nENA s'est arrêté")
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nArrêt d'ENA...")
        ena_process.terminate()
        
    except Exception as e:
        print(f"\nErreur: {str(e)}")
        if 'ena_process' in locals():
            ena_process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()

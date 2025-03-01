import os
import requests
from pathlib import Path
from tqdm import tqdm
import hashlib
import sys

def download_file(url: str, destination: Path, expected_sha256: str = None):
    """Télécharge un fichier avec barre de progression et vérification SHA256"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    # Crée le dossier de destination s'il n'existe pas
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

    sha256_hash = hashlib.sha256()
    
    with open(destination, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
            sha256_hash.update(data)
    
    progress_bar.close()
    
    if expected_sha256:
        calculated_hash = sha256_hash.hexdigest()
        if calculated_hash != expected_sha256:
            print(f"Attention: Le hash SHA256 ne correspond pas pour {destination.name}")
            print(f"Attendu: {expected_sha256}")
            print(f"Calculé: {calculated_hash}")
            return False
    return True

def main():
    # Définition des modèles à télécharger
    models = {
        "mistral-7b-instruct-v0.2": {
            "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
            "filename": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
            "sha256": "None"  # À remplir si nécessaire
        },
        "gpt4all-j": {
            "url": "https://gpt4all.io/models/gguf/gpt4all-j-v1.3-groovy.gguf",
            "filename": "gpt4all-j-v1.3-groovy.gguf",
            "sha256": "None"  # À remplir si nécessaire
        }
    }
    
    # Chemin du dossier models
    models_dir = Path(__file__).parent.parent / "models"
    
    # Création du dossier models s'il n'existe pas
    models_dir.mkdir(exist_ok=True)
    
    print("=== Téléchargement des modèles d'IA ===")
    print(f"Dossier de destination: {models_dir}")
    
    for model_name, model_info in models.items():
        model_path = models_dir / model_info["filename"]
        
        if model_path.exists():
            print(f"\nLe modèle {model_name} existe déjà.")
            size_mb = model_path.stat().st_size / (1024 * 1024)
            print(f"Taille: {size_mb:.2f} MB")
            continue
        
        print(f"\nTéléchargement de {model_name}...")
        try:
            success = download_file(
                model_info["url"],
                model_path,
                model_info["sha256"]
            )
            if success:
                print(f"Téléchargement de {model_name} terminé avec succès!")
            else:
                print(f"Erreur lors du téléchargement de {model_name}")
        except Exception as e:
            print(f"Erreur lors du téléchargement de {model_name}: {str(e)}")

if __name__ == "__main__":
    main()

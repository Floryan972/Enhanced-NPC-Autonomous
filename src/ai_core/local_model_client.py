from pathlib import Path
from typing import Optional
from ctransformers import AutoModelForCausalLM

class LocalModelClient:
    def __init__(self, model_path: str = None):
        """
        Initialise le client avec un modèle local
        model_path: chemin vers le fichier .gguf
        """
        if model_path is None:
            # Cherche automatiquement un modèle .gguf dans le dossier models
            models_dir = Path(__file__).parent.parent.parent / "models"
            gguf_files = list(models_dir.glob("*.gguf"))
            if not gguf_files:
                raise ValueError("Aucun modèle .gguf trouvé dans le dossier models/")
            model_path = str(gguf_files[0])
            print(f"Utilisation automatique du modèle: {model_path}")

        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            model_type="llama",
            gpu_layers=50  # Utilise le GPU si disponible
        )

    async def generate_response(self, 
                              prompt: str,
                              max_tokens: int = 150,
                              temperature: float = 0.7) -> str:
        """
        Génère une réponse en utilisant le modèle local
        """
        try:
            # Formatage du prompt pour de meilleures réponses
            formatted_prompt = f"""### Instruction: Agis comme un PNJ intelligent et autonome. 
Réponds de manière appropriée à ce message :
{prompt}

### Response:"""

            # Génération de la réponse
            response = self.model(
                formatted_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["### Instruction", "### Response"]
            )
            
            return response.strip()
            
        except Exception as e:
            print(f"Erreur lors de la génération: {str(e)}")
            return "Désolé, je ne peux pas générer de réponse pour le moment."

    async def check_connection(self) -> bool:
        """
        Vérifie si le modèle est chargé et fonctionnel
        """
        try:
            # Test simple pour vérifier que le modèle fonctionne
            test_response = self.model("Test", max_tokens=5)
            return True
        except:
            return False

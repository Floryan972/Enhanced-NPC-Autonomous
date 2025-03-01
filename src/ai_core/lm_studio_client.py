import aiohttp
import json
from typing import Dict, Any, Optional

class LMStudioClient:
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json"
        }

    async def generate_response(self, prompt: str, 
                              max_tokens: int = 150,
                              temperature: float = 0.7) -> str:
        """
        Génère une réponse en utilisant l'API LM Studio
        """
        async with aiohttp.ClientSession() as session:
            data = {
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"Erreur API LM Studio: {error_text}")
            except Exception as e:
                print(f"Erreur lors de la génération: {str(e)}")
                return "Désolé, je ne peux pas générer de réponse pour le moment."

    async def check_connection(self) -> bool:
        """
        Vérifie si LM Studio est accessible
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/models") as response:
                    return response.status == 200
        except:
            return False

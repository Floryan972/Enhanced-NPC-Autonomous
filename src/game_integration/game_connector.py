from abc import ABC, abstractmethod
from typing import Dict, Any
import asyncio
import json

class GameConnector(ABC):
    """
    Classe abstraite pour l'intégration avec différents jeux
    """
    def __init__(self, game_name: str, config: Dict[str, Any]):
        self.game_name = game_name
        self.config = config
        self.is_connected = False
        self.game_state = {}

    @abstractmethod
    async def connect(self) -> bool:
        """
        Établit la connexion avec le jeu
        """
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Ferme la connexion avec le jeu
        """
        pass

    @abstractmethod
    async def update_game_state(self, state: Dict[str, Any]):
        """
        Met à jour l'état du jeu
        """
        pass

    @abstractmethod
    async def send_command(self, command: str, params: Dict[str, Any]):
        """
        Envoie une commande au jeu
        """
        pass

class LocalGameConnector(GameConnector):
    """
    Implémentation pour les tests locaux et le prototypage
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__("local_test", config)
        self.event_queue = asyncio.Queue()

    async def connect(self) -> bool:
        self.is_connected = True
        print(f"Connecté au jeu de test local")
        return True

    async def disconnect(self) -> bool:
        self.is_connected = False
        return True

    async def update_game_state(self, state: Dict[str, Any]):
        self.game_state.update(state)
        await self.event_queue.put({
            "type": "state_update",
            "data": state
        })

    async def send_command(self, command: str, params: Dict[str, Any]):
        event = {
            "type": "command",
            "command": command,
            "params": params
        }
        await self.event_queue.put(event)
        print(f"Commande envoyée: {json.dumps(event, indent=2)}")

class NetworkedGameConnector(GameConnector):
    """
    Implémentation pour la connexion réseau avec les jeux
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config["game_name"], config)
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 8080)
        self.protocol = config.get("protocol", "websocket")

    async def connect(self) -> bool:
        try:
            # Implémentation de la connexion réseau ici
            self.is_connected = True
            print(f"Connecté à {self.game_name} sur {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Erreur de connexion: {str(e)}")
            return False

    async def disconnect(self) -> bool:
        # Implémentation de la déconnexion réseau ici
        self.is_connected = False
        return True

    async def update_game_state(self, state: Dict[str, Any]):
        if not self.is_connected:
            raise ConnectionError("Non connecté au jeu")
        # Implémentation de la mise à jour d'état ici
        self.game_state.update(state)

    async def send_command(self, command: str, params: Dict[str, Any]):
        if not self.is_connected:
            raise ConnectionError("Non connecté au jeu")
        # Implémentation de l'envoi de commande ici
        print(f"Envoi de la commande au jeu: {command} avec params: {params}")

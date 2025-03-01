import asyncio
import json
import sys
import os
from pathlib import Path

# Ajout du chemin source au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from src.npc.npc_controller import NPCController
from src.animals.animal_behavior import AnimalBehavior
from src.missions.mission_generator import MissionGenerator
from src.game_integration.game_adapters.skyrim_adapter import SkyrimAdapter
from src.ai_core.local_model_client import LocalModelClient

async def main():
    print("Démarrage de la démonstration Enhanced NPC Autonomous...")
    
    # Initialisation du client avec le modèle local
    model_client = LocalModelClient()  # Va automatiquement chercher un fichier .gguf dans /models
    print("\nChargement du modèle local...")
    
    if not await model_client.check_connection():
        print("Erreur: Impossible de charger le modèle.")
        print("Assurez-vous qu'un fichier .gguf est présent dans le dossier models/")
        return
    
    print("Modèle chargé avec succès!")
    
    # Configuration du jeu
    game_config = {
        "game_name": "Skyrim",
        "host": "localhost",
        "port": 8080
    }
    
    # Initialisation de l'adaptateur de jeu
    game = SkyrimAdapter(game_config)
    print("\nConnexion au jeu...")
    game_connected = await game.connect()
    
    if not game_connected:
        print("Note: Mode simulation sans connexion au jeu")
    
    # Création des PNJ
    merchant = NPCController("merchant_alchemist", model_client)
    guard = NPCController("city_guard", model_client)
    
    # Création des animaux
    wolf_config = {
        "species": "wolf",
        "pack_behavior": True,
        "hunting_style": "pack",
        "prey": ["deer", "rabbit"],
        "predators": ["bear"],
        "territory_size": 1000
    }
    wolf = AnimalBehavior("wolf_pack_alpha", wolf_config, model_client)
    
    # Initialisation du générateur de missions
    mission_gen = MissionGenerator(model_client)
    
    # Simulation d'un monde vivant
    print("\nDémarrage de la simulation...")
    
    # État initial du monde
    world_state = {
        "time_of_day": "morning",
        "weather": "clear",
        "entities": [
            {"type": "player", "position": (0, 0, 0)},
            {"type": "merchant", "position": (10, 0, 0)},
            {"type": "guard", "position": (-5, 0, 0)}
        ],
        "resources": [
            {"type": "herb_patch", "position": (15, 0, 0)},
            {"type": "water_source", "position": (-15, 0, 0)}
        ]
    }
    
    # Démonstration des interactions
    print("\n=== Démonstration des interactions ===")
    
    try:
        # 1. Génération d'une mission
        print("\n1. Génération d'une nouvelle mission...")
        mission = await mission_gen.generate_mission(world_state, difficulty=3)
        print(f"Mission générée: {mission.title}")
        print(f"Description: {mission.description}")
        
        # 2. Interaction avec un PNJ
        print("\n2. Test de dialogue avec le marchand...")
        player_input = "Bonjour, avez-vous des potions de soin ?"
        merchant_response = await merchant.process_dialogue(player_input)
        print(f"Joueur: {player_input}")
        print(f"Marchand: {merchant_response}")
        
        # 3. Comportement animal
        print("\n3. Simulation du comportement des loups...")
        await wolf.update_behavior(world_state)
        print(f"État du loup: {wolf.state.behavior_mode}")
        
        # 4. Réaction du garde à un événement
        print("\n4. Réaction du garde à un événement...")
        event = {
            "type": "crime",
            "severity": "theft",
            "location": (2, 0, 0)
        }
        await guard.update_behavior({**world_state, "event": event})
        
        # 5. Mise à jour de l'état du monde
        print("\n5. Mise à jour de l'état du monde...")
        world_state["time_of_day"] = "afternoon"
        world_state["weather"] = "rainy"
        
        # Mise à jour des comportements avec le nouvel état
        print("\nMise à jour des comportements avec le nouvel état...")
        await asyncio.gather(
            merchant.update_behavior(world_state),
            guard.update_behavior(world_state),
            wolf.update_behavior(world_state)
        )
        
    except Exception as e:
        print(f"\nErreur pendant la démonstration: {str(e)}")
    
    print("\nDémonstration terminée!")

if __name__ == "__main__":
    asyncio.run(main())

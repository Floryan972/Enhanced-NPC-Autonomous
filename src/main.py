import asyncio
from pathlib import Path
import logging
from typing import Dict, Optional
import json
import time

from npc.ai_loader import AILoader
from npc.personality_system import PersonalitySystem
from npc.emotion_system import EmotionSystem
from npc.memory_system import MemorySystem
from npc.knowledge_system import KnowledgeSystem
from npc.routine_system import RoutineSystem
from npc.quest_system import QuestSystem
from npc.combat_system import CombatSystem
from npc.economy_system import EconomySystem
from npc.dialogue_system import DialogueSystem
from npc.faction_system import FactionSystem
from npc.social_system import SocialSystem
from npc.decision_system import DecisionSystem

class EnhancedNPCSystem:
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.loader: Optional[AILoader] = None
        self.systems: Dict = {}
        self.npcs: Dict = {}
        self.world_state: Dict = {
            "time": time.time(),
            "weather": "clear",
            "events": [],
            "active_quests": set(),
            "completed_quests": set(),
            "global_variables": {}
        }
        
        # Configuration du logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('npc_system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("EnhancedNPC")
    
    async def initialize(self):
        """Initialise le système complet"""
        try:
            self.logger.info("Démarrage du système NPC amélioré...")
            
            # Création du chargeur
            self.loader = AILoader(self.data_path)
            
            # Chargement des systèmes et PNJ
            result = await self.loader.load_all()
            self.systems = result["systems"]
            self.npcs = result["npcs"]
            
            # Initialisation du monde
            await self.initialize_world()
            
            self.logger.info(
                f"Initialisation terminée en {result['load_time']:.2f} secondes"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation: {str(e)}")
            return False
    
    async def initialize_world(self):
        """Initialise l'état du monde"""
        try:
            # Chargement de l'état du monde
            world_file = self.data_path / "world_state.json"
            if world_file.exists():
                self.world_state.update(
                    json.loads(world_file.read_text(encoding='utf-8'))
                )
            
            # Mise à jour des PNJ avec l'état du monde
            for npc_id, npc in self.npcs.items():
                await self.update_npc_state(npc_id)
            
            self.logger.info("État du monde initialisé")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation du monde: {str(e)}")
    
    async def update_npc_state(self, npc_id: str):
        """Met à jour l'état d'un PNJ"""
        try:
            npc = self.npcs.get(npc_id)
            if not npc:
                return
            
            # Mise à jour des systèmes du PNJ
            for system_name, system in npc["systems"].items():
                if hasattr(system, "update"):
                    await system.update(self.world_state)
            
            # Vérification des routines
            routine_system = npc["systems"].get("routine")
            if routine_system:
                current_activity = await routine_system.get_current_activity()
                if current_activity:
                    self.logger.debug(
                        f"{npc_id} effectue: {current_activity.name}"
                    )
            
        except Exception as e:
            self.logger.error(
                f"Erreur lors de la mise à jour du PNJ {npc_id}: {str(e)}"
            )
    
    async def update_world(self, delta_time: float):
        """Met à jour l'état du monde"""
        try:
            # Mise à jour du temps
            self.world_state["time"] += delta_time
            
            # Mise à jour des événements
            self.world_state["events"] = [
                event for event in self.world_state["events"]
                if event["time"] > self.world_state["time"]
            ]
            
            # Mise à jour de tous les PNJ
            for npc_id in self.npcs:
                await self.update_npc_state(npc_id)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du monde: {str(e)}")
    
    def get_npc(self, npc_id: str) -> Optional[Dict]:
        """Récupère les données d'un PNJ"""
        return self.npcs.get(npc_id)
    
    def get_system(self, system_name: str):
        """Récupère un système"""
        return self.systems.get(system_name)
    
    async def interact_with_npc(self, npc_id: str, action: str, data: Dict) -> Dict:
        """Interagit avec un PNJ"""
        try:
            npc = self.get_npc(npc_id)
            if not npc:
                return {"success": False, "error": "PNJ non trouvé"}
            
            # Traitement de l'interaction
            if action == "dialogue":
                dialogue_system = npc["systems"].get("dialogue")
                if dialogue_system:
                    response = await dialogue_system.process_dialogue(data)
                    return {"success": True, "response": response}
            
            elif action == "trade":
                economy_system = npc["systems"].get("economy")
                if economy_system:
                    result = await economy_system.process_trade(data)
                    return {"success": True, "result": result}
            
            elif action == "quest":
                quest_system = npc["systems"].get("quest")
                if quest_system:
                    quest = await quest_system.get_available_quest(data)
                    return {"success": True, "quest": quest}
            
            return {"success": False, "error": "Action non supportée"}
            
        except Exception as e:
            self.logger.error(
                f"Erreur lors de l'interaction avec {npc_id}: {str(e)}"
            )
            return {"success": False, "error": str(e)}
    
    async def save_state(self):
        """Sauvegarde l'état du système"""
        try:
            # Sauvegarde de l'état du monde
            world_file = self.data_path / "world_state.json"
            world_file.write_text(
                json.dumps(self.world_state, indent=2),
                encoding='utf-8'
            )
            
            # Sauvegarde des PNJ
            npcs_file = self.data_path / "npcs_state.json"
            npcs_state = {
                npc_id: {
                    "template": npc["template"],
                    "data": npc["data"]
                }
                for npc_id, npc in self.npcs.items()
            }
            npcs_file.write_text(
                json.dumps(npcs_state, indent=2),
                encoding='utf-8'
            )
            
            self.logger.info("État sauvegardé avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
            return False
    
    def shutdown(self):
        """Arrête proprement le système"""
        try:
            # Sauvegarde de l'état
            asyncio.run(self.save_state())
            
            # Fermeture des systèmes
            for system in self.systems.values():
                if hasattr(system, "shutdown"):
                    system.shutdown()
            
            # Fermeture du thread pool
            if self.loader:
                self.loader.executor.shutdown()
            
            self.logger.info("Système arrêté avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'arrêt: {str(e)}")

async def main():
    # Création du système
    npc_system = EnhancedNPCSystem()
    
    try:
        # Initialisation
        if not await npc_system.initialize():
            print("Erreur lors de l'initialisation")
            return
        
        # Boucle principale
        print("Système NPC démarré")
        while True:
            try:
                # Mise à jour du monde
                await npc_system.update_world(1.0)  # Delta time de 1 seconde
                
                # Attente
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                print("\nArrêt demandé...")
                break
            
            except Exception as e:
                print(f"Erreur dans la boucle principale: {str(e)}")
    
    finally:
        # Arrêt propre
        npc_system.shutdown()

if __name__ == "__main__":
    asyncio.run(main())

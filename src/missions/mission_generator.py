from typing import Dict, List, Optional
import random
import json
from dataclasses import dataclass
import asyncio

@dataclass
class MissionObjective:
    description: str
    type: str
    target: Dict
    completion_criteria: Dict
    reward: Dict

@dataclass
class Mission:
    id: str
    title: str
    description: str
    difficulty: int
    objectives: List[MissionObjective]
    prerequisites: Dict
    rewards: Dict
    npc_involved: List[str]

class MissionGenerator:
    def __init__(self, ai_model):
        self.ai_model = ai_model
        self.mission_templates = self._load_mission_templates()
        self.active_missions: Dict[str, Mission] = {}

    def _load_mission_templates(self) -> Dict:
        """Charge les templates de missions depuis un fichier JSON"""
        # À implémenter : chargement depuis un fichier de configuration
        return {
            "investigation": {
                "structure": ["recherche", "interrogation", "résolution"],
                "complexity_factors": ["nombre_suspects", "indices_cachés", "time_pressure"]
            },
            "combat": {
                "structure": ["reconnaissance", "stratégie", "affrontement"],
                "complexity_factors": ["nombre_ennemis", "types_ennemis", "environnement"]
            },
            "exploration": {
                "structure": ["découverte", "puzzle", "récompense"],
                "complexity_factors": ["taille_zone", "dangers", "secrets"]
            }
        }

    async def generate_mission(self, world_state: Dict, difficulty: int) -> Mission:
        """Génère une nouvelle mission basée sur l'état du monde"""
        # Création du prompt pour l'IA
        prompt = self._create_mission_prompt(world_state, difficulty)
        
        # Génération de la mission avec l'IA
        mission_data = await self.ai_model.generate_response(prompt)
        mission_dict = json.loads(mission_data)  # Conversion de la réponse en dict
        
        # Création de la mission
        mission = Mission(
            id=f"mission_{random.randint(1000, 9999)}",
            title=mission_dict["title"],
            description=mission_dict["description"],
            difficulty=difficulty,
            objectives=[
                MissionObjective(**obj) for obj in mission_dict["objectives"]
            ],
            prerequisites=mission_dict["prerequisites"],
            rewards=mission_dict["rewards"],
            npc_involved=mission_dict["npc_involved"]
        )
        
        self.active_missions[mission.id] = mission
        return mission

    def _create_mission_prompt(self, world_state: Dict, difficulty: int) -> str:
        """Crée un prompt pour la génération de mission"""
        return f"""
        Générer une mission complexe avec les paramètres suivants:
        - État du monde: {json.dumps(world_state, indent=2)}
        - Difficulté: {difficulty}
        - Templates disponibles: {json.dumps(self.mission_templates, indent=2)}
        
        La mission doit être unique, non répétitive et inclure:
        1. Des objectifs multiples et interconnectés
        2. Des PNJ avec des motivations complexes
        3. Des choix significatifs
        4. Des récompenses appropriées
        
        Format de sortie attendu: JSON avec les champs title, description, objectives, etc.
        """

    async def update_mission_state(self, mission_id: str, progress: Dict):
        """Met à jour l'état d'une mission en cours"""
        if mission_id not in self.active_missions:
            raise ValueError(f"Mission {mission_id} non trouvée")
            
        mission = self.active_missions[mission_id]
        
        # Analyse du progrès et mise à jour des objectifs
        for objective in mission.objectives:
            if self._check_objective_completion(objective, progress):
                print(f"Objectif complété: {objective.description}")
                
        # Vérification de la completion de la mission
        if self._check_mission_completion(mission):
            await self._complete_mission(mission)

    def _check_objective_completion(self, objective: MissionObjective, progress: Dict) -> bool:
        """Vérifie si un objectif est complété"""
        criteria = objective.completion_criteria
        for key, value in criteria.items():
            if key not in progress or progress[key] < value:
                return False
        return True

    def _check_mission_completion(self, mission: Mission) -> bool:
        """Vérifie si tous les objectifs de la mission sont complétés"""
        # À implémenter : logique de vérification
        return False

    async def _complete_mission(self, mission: Mission):
        """Gère la completion d'une mission"""
        # Distribution des récompenses
        # Mise à jour de l'état du monde
        # Notification des PNJ impliqués
        del self.active_missions[mission.id]

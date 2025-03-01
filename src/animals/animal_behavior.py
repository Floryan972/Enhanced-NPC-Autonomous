from typing import Dict, List, Tuple, Optional
import math
import random
from dataclasses import dataclass
import asyncio

@dataclass
class AnimalState:
    species: str
    health: float
    hunger: float
    energy: float
    position: Tuple[float, float, float]
    behavior_mode: str
    threats: List[Dict]
    pack_members: List[str]

class AnimalBehavior:
    def __init__(self, animal_id: str, species_config: Dict, ai_model):
        self.animal_id = animal_id
        self.species_config = species_config
        self.ai_model = ai_model
        self.state = AnimalState(
            species=species_config["species"],
            health=100.0,
            hunger=0.0,
            energy=100.0,
            position=(0, 0, 0),
            behavior_mode="idle",
            threats=[],
            pack_members=[]
        )
        
        # Chargement des comportements spécifiques à l'espèce
        self.behaviors = self._load_species_behaviors()
        
    def _load_species_behaviors(self) -> Dict:
        """Charge les comportements spécifiques à l'espèce"""
        return {
            "hunting": {
                "prey_types": self.species_config.get("prey", []),
                "hunting_style": self.species_config.get("hunting_style", "solo"),
                "success_rate": self.species_config.get("hunting_success", 0.5)
            },
            "social": {
                "pack_behavior": self.species_config.get("pack_behavior", False),
                "territory_size": self.species_config.get("territory_size", 100),
                "aggression_level": self.species_config.get("aggression", 0.3)
            },
            "daily_routine": {
                "active_hours": self.species_config.get("active_hours", ["day"]),
                "sleep_duration": self.species_config.get("sleep_duration", 8),
                "feeding_frequency": self.species_config.get("feeding_freq", 3)
            }
        }

    async def update_behavior(self, world_state: Dict):
        """Met à jour le comportement de l'animal en fonction de l'environnement"""
        # Analyse de l'environnement
        threats = self._detect_threats(world_state)
        opportunities = self._detect_opportunities(world_state)
        
        # Création du contexte pour l'IA
        context = {
            "animal_state": self.state.__dict__,
            "environment": world_state,
            "threats": threats,
            "opportunities": opportunities,
            "behaviors": self.behaviors
        }
        
        # Génération de la décision avec l'IA
        decision = await self._generate_behavior_decision(context)
        
        # Application de la décision
        await self._apply_behavior_decision(decision)

    def _detect_threats(self, world_state: Dict) -> List[Dict]:
        """Détecte les menaces dans l'environnement"""
        threats = []
        for entity in world_state.get("entities", []):
            if self._is_threat(entity):
                threat = {
                    "type": entity["type"],
                    "distance": self._calculate_distance(self.state.position, entity["position"]),
                    "danger_level": self._evaluate_danger(entity)
                }
                threats.append(threat)
        return threats

    def _detect_opportunities(self, world_state: Dict) -> List[Dict]:
        """Détecte les opportunités (nourriture, eau, abri, etc.)"""
        opportunities = []
        for resource in world_state.get("resources", []):
            if self._is_relevant_resource(resource):
                opportunity = {
                    "type": resource["type"],
                    "distance": self._calculate_distance(self.state.position, resource["position"]),
                    "value": self._evaluate_resource_value(resource)
                }
                opportunities.append(opportunity)
        return opportunities

    async def _generate_behavior_decision(self, context: Dict) -> Dict:
        """Génère une décision de comportement basée sur le contexte"""
        prompt = self._create_behavior_prompt(context)
        response = await self.ai_model.generate_response(prompt)
        return self._parse_behavior_response(response)

    def _create_behavior_prompt(self, context: Dict) -> str:
        """Crée un prompt pour la génération de comportement"""
        return f"""
        Générer un comportement réaliste pour un {self.state.species} avec:
        - État actuel: {context['animal_state']}
        - Menaces détectées: {context['threats']}
        - Opportunités: {context['opportunities']}
        - Comportements disponibles: {context['behaviors']}
        
        Le comportement doit être:
        1. Réaliste pour l'espèce
        2. Adapté à la situation
        3. Prendre en compte les besoins de survie
        4. Considérer le comportement social si applicable
        
        Format de sortie attendu: JSON avec action, paramètres et justification
        """

    async def _apply_behavior_decision(self, decision: Dict):
        """Applique la décision de comportement"""
        action = decision.get("action")
        params = decision.get("parameters", {})
        
        if action == "move":
            await self._move_to(params["destination"])
        elif action == "hunt":
            await self._initiate_hunt(params["target"])
        elif action == "flee":
            await self._flee_from(params["threat"])
        elif action == "rest":
            await self._rest(params["duration"])
        elif action == "social":
            await self._social_interaction(params["target"], params["type"])

    # Méthodes utilitaires
    def _calculate_distance(self, pos1: Tuple[float, float, float], 
                          pos2: Tuple[float, float, float]) -> float:
        """Calcule la distance entre deux points"""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(pos1, pos2)))

    def _is_threat(self, entity: Dict) -> bool:
        """Détermine si une entité est une menace"""
        return entity["type"] in self.species_config.get("predators", [])

    def _is_relevant_resource(self, resource: Dict) -> bool:
        """Détermine si une ressource est pertinente"""
        return resource["type"] in self.species_config.get("resources", [])

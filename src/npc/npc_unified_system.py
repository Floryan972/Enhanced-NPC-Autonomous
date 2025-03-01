"""
Système NPC unifié pour STALKER 2
Ce module combine tous les sous-systèmes NPC en un système cohérent et puissant.
"""

from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum, auto
import logging
import uuid
import json
import random
from datetime import datetime, time
import math
from pathlib import Path

# États et types énumérés
class NPCStateType(Enum):
    IDLE = auto()
    MOVING = auto()
    COMBAT = auto()
    INTERACTING = auto()
    TRADING = auto()
    CRAFTING = auto()
    RESTING = auto()
    INVESTIGATING = auto()
    FLEEING = auto()

class EmotionType(Enum):
    FEAR = auto()
    ANGER = auto()
    JOY = auto()
    SADNESS = auto()
    TRUST = auto()
    DISGUST = auto()
    SURPRISE = auto()
    ANTICIPATION = auto()

class RelationType(Enum):
    FRIEND = auto()
    ENEMY = auto()
    NEUTRAL = auto()
    ALLY = auto()
    RIVAL = auto()

# Classes de données principales
@dataclass
class NPCState:
    """État complet d'un PNJ"""
    id: str
    position: Dict[str, float]
    health: float = 100.0
    inventory: Dict[str, Any] = field(default_factory=dict)
    relationships: Dict[str, float] = field(default_factory=dict)
    knowledge_base: Dict[str, Any] = field(default_factory=dict)
    emotional_state: Dict[str, float] = field(default_factory=dict)
    active_effects: List[Dict[str, Any]] = field(default_factory=list)
    state_type: NPCStateType = NPCStateType.IDLE
    personality_traits: Dict[str, float] = field(default_factory=dict)
    skills: Dict[str, float] = field(default_factory=dict)
    faction: Optional[str] = None
    current_quest: Optional[str] = None
    daily_schedule: Dict[str, Any] = field(default_factory=dict)
    memory: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.emotional_state:
            self.emotional_state = {
                'fear': 0.0,
                'anger': 0.0,
                'joy': 0.5,
                'trust': 0.5,
                'surprise': 0.0
            }
        if not self.personality_traits:
            self.personality_traits = {
                'aggression': random.uniform(0.2, 0.8),
                'courage': random.uniform(0.3, 0.9),
                'loyalty': random.uniform(0.4, 0.9),
                'curiosity': random.uniform(0.3, 0.8)
            }

@dataclass
class Quest:
    """Structure de quête"""
    id: str
    title: str
    description: str
    objectives: List[Dict[str, Any]]
    rewards: Dict[str, Any]
    status: str = "inactive"
    progress: Dict[str, Any] = field(default_factory=dict)

class UnifiedNPCSystem:
    """
    Système unifié pour la gestion des PNJ
    Combine tous les sous-systèmes en une interface cohérente
    """
    
    def __init__(self, model_manager=None):
        self.logger = logging.getLogger(__name__)
        self.model_manager = model_manager
        self.npcs: Dict[str, NPCState] = {}
        self.quests: Dict[str, Quest] = {}
        self.factions: Dict[str, Dict[str, Any]] = {}
        self.global_state: Dict[str, Any] = {
            'time': datetime.now(),
            'weather': 'clear',
            'global_events': []
        }
        
        # Initialisation des systèmes
        self._init_systems()
        
    def _init_systems(self):
        """Initialise tous les sous-systèmes"""
        self.cooldowns = {}
        self.relationship_cache = {}
        self.combat_states = {}
        self.trading_sessions = {}
        self.crafting_queue = []
        self.dialogue_history = {}
        
    # Gestion des PNJ
    def create_npc(self, npc_data: Dict[str, Any]) -> str:
        """Crée un nouveau PNJ avec les données spécifiées"""
        npc_id = str(uuid.uuid4())
        npc_state = NPCState(
            id=npc_id,
            position=npc_data.get('position', {'x': 0, 'y': 0, 'z': 0}),
            health=npc_data.get('health', 100.0),
            faction=npc_data.get('faction'),
            personality_traits=npc_data.get('personality_traits', {})
        )
        self.npcs[npc_id] = npc_state
        return npc_id

    def update_npc(self, npc_id: str, game_state: Dict[str, Any]) -> None:
        """Met à jour l'état d'un PNJ"""
        if npc_id not in self.npcs:
            self.logger.warning(f"NPC {npc_id} non trouvé")
            return
            
        npc = self.npcs[npc_id]
        
        # Mise à jour de l'état émotionnel
        self._update_emotional_state(npc, game_state)
        
        # Mise à jour des relations
        self._update_relationships(npc, game_state)
        
        # Mise à jour des compétences
        self._update_skills(npc, game_state)
        
        # Gestion des quêtes
        self._process_quests(npc, game_state)
        
        # Mise à jour de la mémoire
        self._update_memory(npc, game_state)

    def _update_emotional_state(self, npc: NPCState, game_state: Dict[str, Any]) -> None:
        """Met à jour l'état émotionnel du PNJ"""
        # Facteurs de base
        health_ratio = npc.health / 100.0
        danger_level = self._calculate_danger_level(npc, game_state)
        
        # Ajustement des émotions
        npc.emotional_state['fear'] = min(1.0, danger_level * (1.0 - health_ratio) + 0.2)
        npc.emotional_state['anger'] = min(1.0, danger_level * npc.personality_traits.get('aggression', 0.5))
        
        # Mise à jour de l'état en fonction des menaces
        if game_state.get('in_combat') and danger_level > 0.3:
            npc.state_type = NPCStateType.COMBAT
        elif npc.health < 30:
            npc.state_type = NPCStateType.FLEEING
        
        # Influence des alliés proches
        nearby_allies = self._get_nearby_allies(npc, game_state)
        if nearby_allies:
            npc.emotional_state['trust'] = min(1.0, npc.emotional_state['trust'] + 0.1 * len(nearby_allies))

    def _update_relationships(self, npc: NPCState, game_state: Dict[str, Any]) -> None:
        """Met à jour les relations du PNJ"""
        for interaction in game_state.get('recent_interactions', []):
            target_id = interaction.get('target_id')
            if target_id and target_id in self.npcs:
                # Impact basé sur le type d'interaction
                impact = self._calculate_interaction_impact(interaction)
                current_relation = npc.relationships.get(target_id, 0.0)
                npc.relationships[target_id] = max(-1.0, min(1.0, current_relation + impact))

    def _update_skills(self, npc: NPCState, game_state: Dict[str, Any]) -> None:
        """Met à jour les compétences du PNJ"""
        for action in game_state.get('recent_actions', []):
            skill_type = action.get('skill_type')
            if skill_type and skill_type in npc.skills:
                success = action.get('success', False)
                difficulty = action.get('difficulty', 1.0)
                
                # Calcul du gain de compétence
                skill_gain = 0.01 * difficulty * (1.0 if success else 0.5)
                npc.skills[skill_type] = min(1.0, npc.skills[skill_type] + skill_gain)

    def _process_quests(self, npc: NPCState, game_state: Dict[str, Any]) -> None:
        """Traite les quêtes actives du PNJ"""
        if npc.current_quest and npc.current_quest in self.quests:
            quest = self.quests[npc.current_quest]
            
            # Vérification des objectifs
            for objective in quest.objectives:
                if objective['status'] == 'active':
                    if self._check_objective_completion(npc, objective, game_state):
                        objective['status'] = 'completed'
                        self._grant_objective_rewards(npc, objective)

    def _check_objective_completion(self, npc: NPCState, objective: Dict[str, Any], game_state: Dict[str, Any]) -> bool:
        """Vérifie si un objectif est complété"""
        objective_type = objective.get('type')
        if objective_type == 'explore':
            location = objective.get('location', {})
            npc_pos = game_state.get('position', npc.position)  # Utilise la position du game_state si disponible
            distance = self._calculate_distance(npc_pos, location.get('position', {}))
            return distance < location.get('radius', 10.0)
        return False

    def _update_memory(self, npc: NPCState, game_state: Dict[str, Any]) -> None:
        """Met à jour la mémoire du PNJ"""
        # Création d'un nouveau souvenir
        memory_entry = {
            'timestamp': str(datetime.now()),
            'location': npc.position.copy(),
            'emotional_state': npc.emotional_state.copy(),
            'significant_events': game_state.get('significant_events', [])
        }
        
        # Ajout à la mémoire avec limite de taille
        npc.memory.append(memory_entry)
        if len(npc.memory) > 100:  # Limite arbitraire
            npc.memory.pop(0)

    # Utilitaires
    def _calculate_danger_level(self, npc: NPCState, game_state: Dict[str, Any]) -> float:
        """Calcule le niveau de danger pour un PNJ"""
        danger_level = 0.0
        
        # Menaces directes
        for threat in game_state.get('threats', []):
            distance = self._calculate_distance(npc.position, threat.get('position', {}))
            threat_level = threat.get('level', 0.0)
            if distance < 100:  # Distance arbitraire
                danger_level += threat_level * (1.0 - distance/100)
        
        # Conditions environnementales
        if game_state.get('radiation_level'):
            danger_level += game_state['radiation_level'] * 0.5
            
        return min(1.0, danger_level)

    def _calculate_distance(self, pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
        """Calcule la distance entre deux positions"""
        return math.sqrt(
            (pos1.get('x', 0) - pos2.get('x', 0))**2 +
            (pos1.get('y', 0) - pos2.get('y', 0))**2 +
            (pos1.get('z', 0) - pos2.get('z', 0))**2
        )

    def _get_nearby_allies(self, npc: NPCState, game_state: Dict[str, Any]) -> List[str]:
        """Trouve les alliés proches du PNJ"""
        nearby_allies = []
        for other_id, other_npc in self.npcs.items():
            if other_id != npc.id:
                distance = self._calculate_distance(npc.position, other_npc.position)
                relation = npc.relationships.get(other_id, 0.0)
                if distance < 50 and relation > 0.5:  # Valeurs arbitraires
                    nearby_allies.append(other_id)
        return nearby_allies

    def _calculate_interaction_impact(self, interaction: Dict[str, Any]) -> float:
        """Calcule l'impact d'une interaction sur la relation"""
        impact_map = {
            'help': 0.1,
            'attack': -0.2,
            'trade': 0.05,
            'betray': -0.3,
            'gift': 0.15
        }
        return impact_map.get(interaction.get('type', 'neutral'), 0.0)

    def _grant_objective_rewards(self, npc: NPCState, objective: Dict[str, Any]) -> None:
        """Accorde les récompenses d'un objectif"""
        rewards = objective.get('rewards', {})
        
        # Items
        for item_id, count in rewards.get('items', {}).items():
            npc.inventory[item_id] = npc.inventory.get(item_id, 0) + count
            
        # Expérience
        if 'experience' in rewards:
            for skill, exp in rewards['experience'].items():
                npc.skills[skill] = min(1.0, npc.skills.get(skill, 0.0) + exp)

    def _is_location_explored(self, npc: NPCState, location: Dict[str, Any]) -> bool:
        """Vérifie si une location a été explorée"""
        if not location:
            return False
            
        npc_pos = npc.position
        location_pos = location.get('position', {})
        distance = self._calculate_distance(npc_pos, location_pos)
        return distance < location.get('radius', 10.0)

    # Interface publique
    def get_npc_state(self, npc_id: str) -> Optional[NPCState]:
        """Récupère l'état complet d'un PNJ"""
        return self.npcs.get(npc_id)

    def get_faction_relations(self, faction_id: str) -> Dict[str, float]:
        """Récupère les relations d'une faction"""
        return self.factions.get(faction_id, {}).get('relations', {})

    def update_global_state(self, new_state: Dict[str, Any]) -> None:
        """Met à jour l'état global du monde"""
        self.global_state.update(new_state)
        
        # Mise à jour de tous les PNJ affectés
        for npc in self.npcs.values():
            self.update_npc(npc.id, new_state)

    def save_state(self, filepath: str) -> None:
        """Sauvegarde l'état du système"""
        state = {
            'npcs': {npc_id: self._serialize_npc(npc) for npc_id, npc in self.npcs.items()},
            'quests': self.quests,
            'factions': self.factions,
            'global_state': self.global_state
        }
        
        # Conversion des dates en chaînes ISO
        def datetime_handler(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f'Object of type {type(obj)} is not JSON serializable')
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=datetime_handler)

    def load_state(self, filepath: str) -> None:
        """Charge l'état du système"""
        with open(filepath, 'r') as f:
            state = json.load(f)
            
        self.npcs = {npc_id: self._deserialize_npc(npc_data) 
                    for npc_id, npc_data in state['npcs'].items()}
        self.quests = state['quests']
        self.factions = state['factions']
        self.global_state = state['global_state']

    def _serialize_npc(self, npc: NPCState) -> Dict[str, Any]:
        """Sérialise un PNJ pour la sauvegarde"""
        return {
            'id': npc.id,
            'position': npc.position,
            'health': npc.health,
            'inventory': npc.inventory,
            'relationships': npc.relationships,
            'knowledge_base': npc.knowledge_base,
            'emotional_state': npc.emotional_state,
            'active_effects': npc.active_effects,
            'state_type': npc.state_type.name,
            'personality_traits': npc.personality_traits,
            'skills': npc.skills,
            'faction': npc.faction,
            'current_quest': npc.current_quest,
            'daily_schedule': npc.daily_schedule,
            'memory': npc.memory
        }

    def _deserialize_npc(self, data: Dict[str, Any]) -> NPCState:
        """Désérialise un PNJ depuis la sauvegarde"""
        return NPCState(
            id=data['id'],
            position=data['position'],
            health=data['health'],
            inventory=data['inventory'],
            relationships=data['relationships'],
            knowledge_base=data['knowledge_base'],
            emotional_state=data['emotional_state'],
            active_effects=data['active_effects'],
            state_type=NPCStateType[data['state_type']],
            personality_traits=data['personality_traits'],
            skills=data['skills'],
            faction=data['faction'],
            current_quest=data['current_quest'],
            daily_schedule=data['daily_schedule'],
            memory=data['memory']
        )

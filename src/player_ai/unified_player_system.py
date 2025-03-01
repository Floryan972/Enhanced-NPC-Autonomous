"""
Système Unifié de Contrôle du Joueur pour STALKER 2
Combine le système autonome et le contrôleur en un seul module.
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum, auto
from dataclasses import dataclass, field
import logging
import json
import math
from datetime import datetime
from pathlib import Path

# États et Objectifs du Joueur
class PlayerState(Enum):
    MANUAL = auto()  # Contrôlé par le joueur
    AI_CONTROLLED = auto()  # Contrôlé par l'IA
    TRANSITION = auto()  # En transition entre les deux modes

class PlayerObjective(Enum):
    EXPLORE = auto()  # Explorer la zone
    COMBAT = auto()  # Engager le combat
    LOOT = auto()  # Récupérer des objets
    QUEST = auto()  # Suivre une quête
    TRADE = auto()  # Commercer avec les PNJ
    HEAL = auto()  # Se soigner
    HIDE = auto()  # Se cacher/éviter le danger
    INTERACT = auto()  # Interagir avec PNJ/objets

# Classes de données
@dataclass
class WorldKnowledge:
    """Base de connaissances du monde pour l'IA"""
    known_locations: Dict[str, Dict] = field(default_factory=dict)
    known_npcs: Dict[str, Dict] = field(default_factory=dict)
    known_anomalies: Dict[str, Dict] = field(default_factory=dict)
    quest_knowledge: Dict[str, Dict] = field(default_factory=dict)
    item_knowledge: Dict[str, Dict] = field(default_factory=dict)
    danger_zones: Dict[str, float] = field(default_factory=dict)
    safe_zones: Dict[str, Dict] = field(default_factory=dict)
    trading_spots: Dict[str, Dict] = field(default_factory=dict)

@dataclass
class PlayerContext:
    """Contexte actuel du joueur"""
    health: float = 100.0
    stamina: float = 100.0
    radiation: float = 0.0
    inventory: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, float] = field(default_factory=lambda: {'x': 0, 'y': 0, 'z': 0})
    current_quest: Optional[str] = None
    equipped_items: Dict[str, str] = field(default_factory=dict)
    status_effects: List[Dict] = field(default_factory=list)
    nearby_threats: List[Dict] = field(default_factory=list)
    current_objective: Optional[PlayerObjective] = None

class PlayerAutonomousSystem:
    """Système principal pour le contrôle autonome du joueur"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.state = PlayerState.MANUAL
        self.context = PlayerContext()
        self.knowledge = WorldKnowledge()
        self.decision_weights = {
            'health': 0.8,
            'threat': 0.9,
            'quest': 0.7,
            'loot': 0.5,
            'exploration': 0.4
        }
        self.action_cooldowns = {}
        self.behavioral_profile = {
            'aggression': 0.5,
            'caution': 0.7,
            'curiosity': 0.6,
            'greed': 0.4
        }
        
    def toggle_ai_control(self) -> bool:
        """Active ou désactive le contrôle par l'IA"""
        if self.state == PlayerState.MANUAL:
            self.state = PlayerState.AI_CONTROLLED
            self.logger.info("IA activée - Prise de contrôle du personnage")
            return True
        elif self.state == PlayerState.AI_CONTROLLED:
            self.state = PlayerState.MANUAL
            self.logger.info("IA désactivée - Retour au contrôle manuel")
            return False
            
    def update(self, game_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour l'état et prend des décisions"""
        self._update_context(game_state)
        
        if self.state != PlayerState.AI_CONTROLLED:
            return None
            
        threat_level = self._evaluate_threat_level()
        objectives = self._determine_objectives()
        action = self._decide_action(threat_level, objectives)
        return self._prepare_action(action)
        
    def _update_context(self, game_state: Dict[str, Any]) -> None:
        """Met à jour le contexte avec l'état du jeu"""
        self.context.health = game_state.get('health', self.context.health)
        self.context.stamina = game_state.get('stamina', self.context.stamina)
        self.context.radiation = game_state.get('radiation', self.context.radiation)
        self.context.position = game_state.get('position', self.context.position)
        self.context.nearby_threats = game_state.get('threats', [])
        
        if 'inventory' in game_state:
            self.context.inventory = game_state['inventory']
        
        if 'discovered_locations' in game_state:
            for loc in game_state['discovered_locations']:
                self.knowledge.known_locations[loc['id']] = loc
                
        if 'nearby_npcs' in game_state:
            for npc in game_state['nearby_npcs']:
                self.knowledge.known_npcs[npc['id']] = npc
                
    def _evaluate_threat_level(self) -> float:
        """Évalue le niveau de menace actuel"""
        threat_level = 0.0
        
        for threat in self.context.nearby_threats:
            distance = self._calculate_distance(self.context.position, threat.get('position', {}))
            threat_value = threat.get('danger_level', 0.5)
            if distance < 50:
                threat_level += threat_value * (1.0 - distance/50)
                
        if self.context.radiation > 0.5:
            threat_level += self.context.radiation * 0.3
            
        if self.context.health < 50:
            threat_level += (50 - self.context.health) / 50 * 0.5
            
        return min(1.0, threat_level)
        
    def _determine_objectives(self) -> List[Tuple[PlayerObjective, float]]:
        """Détermine et priorise les objectifs"""
        objectives = []
        
        if self.context.health < 40:
            objectives.append((PlayerObjective.HEAL, 0.9))
            
        if self.context.nearby_threats and self.context.health > 60:
            combat_priority = 0.7 * self.behavioral_profile['aggression']
            objectives.append((PlayerObjective.COMBAT, combat_priority))
            
        if self.context.current_quest:
            quest_data = self.knowledge.quest_knowledge.get(self.context.current_quest, {})
            if quest_data.get('priority', 0) > 0:
                objectives.append((PlayerObjective.QUEST, 0.6))
                
        if len(self.knowledge.known_locations) < 10:
            explore_priority = 0.4 * self.behavioral_profile['curiosity']
            objectives.append((PlayerObjective.EXPLORE, explore_priority))
            
        return sorted(objectives, key=lambda x: x[1], reverse=True)
        
    def _decide_action(self, threat_level: float, objectives: List[Tuple[PlayerObjective, float]]) -> Dict[str, Any]:
        """Décide de la prochaine action"""
        if not objectives:
            return {'type': 'explore', 'params': {'radius': 50}}
            
        primary_objective = objectives[0][0]
        
        if primary_objective == PlayerObjective.HEAL:
            return self._plan_healing_action()
        elif primary_objective == PlayerObjective.COMBAT:
            return self._plan_combat_action(threat_level)
        elif primary_objective == PlayerObjective.QUEST:
            return self._plan_quest_action()
        elif primary_objective == PlayerObjective.EXPLORE:
            return self._plan_exploration_action()
            
        return {'type': 'wait', 'params': {}}
        
    def _plan_healing_action(self) -> Dict[str, Any]:
        """Planifie une action de soin"""
        medkits = [item for item, data in self.context.inventory.items() 
                  if data.get('type') == 'medkit']
        
        if medkits:
            return {
                'type': 'use_item',
                'params': {
                    'item_id': self.context.inventory[medkits[0]]['id'],
                    'target': 'self'
                }
            }
            
        safe_spot = self._find_nearest_safe_spot()
        if safe_spot:
            return {
                'type': 'move_to',
                'params': {
                    'position': safe_spot['position'],
                    'stealth': True
                }
            }
            
        return {'type': 'retreat', 'params': {'direction': 'away_from_threats'}}
        
    def _plan_combat_action(self, threat_level: float) -> Dict[str, Any]:
        """Planifie une action de combat"""
        if not self.context.nearby_threats:
            return {'type': 'explore', 'params': {}}
            
        primary_threat = self.context.nearby_threats[0]
        distance = self._calculate_distance(self.context.position, primary_threat['position'])
        weapon = self._select_best_weapon(distance)
        
        if weapon:
            if distance > weapon.get('optimal_range', 10):
                return {
                    'type': 'move_to',
                    'params': {
                        'position': primary_threat['position'],
                        'keep_distance': weapon['optimal_range']
                    }
                }
            else:
                return {
                    'type': 'attack',
                    'params': {
                        'target': primary_threat['id'],
                        'weapon': weapon['id']
                    }
                }
                
        return {'type': 'retreat', 'params': {'direction': 'away_from_threats'}}
        
    def _plan_quest_action(self) -> Dict[str, Any]:
        """Planifie une action liée à la quête"""
        if not self.context.current_quest:
            return {'type': 'explore', 'params': {}}
            
        quest_data = self.knowledge.quest_knowledge[self.context.current_quest]
        objective = quest_data.get('current_objective')
        
        if not objective:
            return {'type': 'explore', 'params': {}}
            
        if objective['type'] == 'reach_location':
            return {
                'type': 'move_to',
                'params': {
                    'position': objective['position'],
                    'stealth': self.behavioral_profile['caution'] > 0.6
                }
            }
        elif objective['type'] == 'find_item':
            return {
                'type': 'search_area',
                'params': {
                    'item_type': objective['item_type'],
                    'radius': 50
                }
            }
        elif objective['type'] == 'eliminate_target':
            return self._plan_combat_action(0.7)
            
        return {'type': 'wait', 'params': {}}
        
    def _plan_exploration_action(self) -> Dict[str, Any]:
        """Planifie une action d'exploration"""
        unexplored_areas = self._find_unexplored_areas()
        
        if unexplored_areas:
            target_area = unexplored_areas[0]
            return {
                'type': 'explore_area',
                'params': {
                    'position': target_area['position'],
                    'radius': 50,
                    'stealth': self.behavioral_profile['caution'] > 0.5
                }
            }
            
        return {
            'type': 'random_explore',
            'params': {
                'radius': 100,
                'avoid_dangers': True
            }
        }
        
    def _calculate_distance(self, pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
        """Calcule la distance entre deux positions"""
        return math.sqrt(
            (pos1.get('x', 0) - pos2.get('x', 0))**2 +
            (pos1.get('y', 0) - pos2.get('y', 0))**2 +
            (pos1.get('z', 0) - pos2.get('z', 0))**2
        )
        
    def _find_nearest_safe_spot(self) -> Optional[Dict[str, Any]]:
        """Trouve l'abri sûr le plus proche"""
        if not self.knowledge.safe_zones:
            return None
            
        nearest = None
        min_distance = float('inf')
        
        for safe_zone in self.knowledge.safe_zones.values():
            dist = self._calculate_distance(self.context.position, safe_zone['position'])
            if dist < min_distance:
                min_distance = dist
                nearest = safe_zone
                
        return nearest
        
    def _select_best_weapon(self, distance: float) -> Optional[Dict[str, Any]]:
        """Sélectionne la meilleure arme pour la distance donnée"""
        weapons = [item for item in self.context.inventory.values() 
                  if item.get('category') == 'weapon' and item.get('ammo', 0) > 0]
                  
        if not weapons:
            return None
            
        scored_weapons = []
        for weapon in weapons:
            optimal_range = weapon.get('optimal_range', 10)
            range_score = 1.0 - abs(distance - optimal_range) / optimal_range
            damage_score = weapon.get('damage', 0) / 100
            scored_weapons.append((weapon, range_score * damage_score))
            
        if not scored_weapons:
            return None
            
        return max(scored_weapons, key=lambda x: x[1])[0]
        
    def _find_unexplored_areas(self) -> List[Dict[str, Any]]:
        """Trouve les zones inexplorées"""
        grid_size = 100
        explored_positions = set()
        
        for location in self.knowledge.known_locations.values():
            pos = location['position']
            grid_x = int(pos['x'] / grid_size)
            grid_y = int(pos['z'] / grid_size)
            explored_positions.add((grid_x, grid_y))
            
        unexplored = []
        current_pos = self.context.position
        current_grid_x = int(current_pos['x'] / grid_size)
        current_grid_y = int(current_pos['z'] / grid_size)
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                grid_pos = (current_grid_x + dx, current_grid_y + dy)
                if grid_pos not in explored_positions:
                    unexplored.append({
                        'position': {
                            'x': grid_pos[0] * grid_size + grid_size/2,
                            'y': current_pos['y'],
                            'z': grid_pos[1] * grid_size + grid_size/2
                        }
                    })
                    
        return sorted(unexplored,
                     key=lambda x: self._calculate_distance(current_pos, x['position']))
                     
    def _prepare_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare l'action pour l'exécution"""
        action['timestamp'] = datetime.now().isoformat()
        action['context'] = {
            'health': self.context.health,
            'position': self.context.position,
            'threats': len(self.context.nearby_threats)
        }
        
        action_type = action['type']
        if action_type in self.action_cooldowns:
            last_use = self.action_cooldowns[action_type]
            if (datetime.now() - last_use).total_seconds() < 1.0:
                return {'type': 'wait', 'params': {}}
                
        self.action_cooldowns[action_type] = datetime.now()
        return action

class UnifiedPlayerController:
    """Contrôleur unifié pour la gestion du joueur"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ai_system = PlayerAutonomousSystem()
        self.transition_time = 1.0
        self.transition_progress = 0.0
        
    def toggle_ai_mode(self) -> bool:
        """Bascule entre le mode manuel et IA"""
        return self.ai_system.toggle_ai_control()
        
    def update(self, game_state: Dict[str, Any], delta_time: float) -> Optional[Dict[str, Any]]:
        """Met à jour le contrôleur"""
        if self.ai_system.state == PlayerState.TRANSITION:
            self.transition_progress += delta_time
            if self.transition_progress >= self.transition_time:
                self.transition_progress = 0.0
                self.ai_system.state = PlayerState.AI_CONTROLLED
                
        if self.ai_system.state == PlayerState.AI_CONTROLLED:
            return self.ai_system.update(game_state)
            
        return None
        
    def get_current_state(self) -> Dict[str, Any]:
        """Retourne l'état actuel"""
        return {
            'mode': self.ai_system.state.name,
            'transition_progress': self.transition_progress / self.transition_time if self.ai_system.state == PlayerState.TRANSITION else 1.0,
            'ai_active': self.ai_system.state == PlayerState.AI_CONTROLLED
        }
        
    def get_ai_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'IA"""
        if self.ai_system.state != PlayerState.AI_CONTROLLED:
            return {}
            
        return {
            'current_objective': self.ai_system.context.current_objective.name if self.ai_system.context.current_objective else None,
            'health': self.ai_system.context.health,
            'nearby_threats': len(self.ai_system.context.nearby_threats),
            'known_locations': len(self.ai_system.knowledge.known_locations),
            'behavioral_profile': self.ai_system.behavioral_profile
        }

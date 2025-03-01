"""
Tests pour le système unifié de contrôle du joueur
"""

import pytest
from datetime import datetime
from src.player_ai.unified_player_system import (
    UnifiedPlayerController,
    PlayerState,
    PlayerObjective,
    PlayerContext,
    WorldKnowledge
)

@pytest.fixture
def controller():
    """Fixture pour le contrôleur unifié"""
    return UnifiedPlayerController()

@pytest.fixture
def game_state():
    """Fixture pour l'état du jeu de base"""
    return {
        'health': 100,
        'stamina': 100,
        'radiation': 0,
        'position': {'x': 0, 'y': 0, 'z': 0},
        'inventory': {
            'medkit1': {'id': 'medkit1', 'type': 'medkit'},
            'weapon1': {
                'id': 'weapon1',
                'category': 'weapon',
                'optimal_range': 20,
                'damage': 50,
                'ammo': 30
            }
        },
        'threats': []
    }

def test_controller_initialization(controller):
    """Teste l'initialisation du contrôleur"""
    assert controller.ai_system.state == PlayerState.MANUAL
    assert controller.transition_time == 1.0
    assert controller.transition_progress == 0.0

def test_toggle_ai_mode(controller):
    """Teste le basculement entre modes manuel et IA"""
    # Active l'IA
    assert controller.toggle_ai_mode() == True
    assert controller.get_current_state()['ai_active'] == True
    
    # Désactive l'IA
    assert controller.toggle_ai_mode() == False
    assert controller.get_current_state()['ai_active'] == False

def test_context_update(controller, game_state):
    """Teste la mise à jour du contexte"""
    controller.ai_system.update(game_state)
    
    context = controller.ai_system.context
    assert context.health == 100
    assert context.stamina == 100
    assert context.radiation == 0
    assert context.position == {'x': 0, 'y': 0, 'z': 0}
    assert len(context.inventory) == 2
    assert 'medkit1' in context.inventory

def test_threat_evaluation(controller, game_state):
    """Teste l'évaluation des menaces"""
    # Sans menace
    controller.ai_system.update(game_state)
    assert controller.ai_system._evaluate_threat_level() == 0.0
    
    # Avec menace proche
    game_state['threats'] = [{
        'position': {'x': 10, 'y': 0, 'z': 0},
        'danger_level': 0.8
    }]
    controller.ai_system.update(game_state)
    threat_level = controller.ai_system._evaluate_threat_level()
    assert threat_level > 0.0
    assert threat_level <= 1.0

def test_healing_behavior(controller, game_state):
    """Teste le comportement de soin"""
    # Situation critique
    game_state['health'] = 30
    controller.toggle_ai_mode()
    controller.ai_system.update(game_state)
    
    objectives = controller.ai_system._determine_objectives()
    assert objectives[0][0] == PlayerObjective.HEAL
    
    action = controller.ai_system._plan_healing_action()
    assert action['type'] == 'use_item'
    assert action['params']['item_id'] == 'medkit1'

def test_combat_behavior(controller, game_state):
    """Teste le comportement en combat"""
    game_state['threats'] = [{
        'id': 'enemy1',
        'position': {'x': 15, 'y': 0, 'z': 0},
        'danger_level': 0.7
    }]
    controller.toggle_ai_mode()
    
    action = controller.update(game_state, 0.1)
    assert action is not None
    assert action['type'] in ['attack', 'move_to']
    
    if action['type'] == 'attack':
        assert action['params']['target'] == 'enemy1'
        assert action['params']['weapon'] == 'weapon1'
    else:  # move_to
        assert 'position' in action['params']
        assert 'keep_distance' in action['params']

def test_exploration_behavior(controller, game_state):
    """Teste le comportement d'exploration"""
    controller.toggle_ai_mode()
    action = controller.ai_system._plan_exploration_action()
    
    assert action['type'] in ['explore_area', 'random_explore']
    assert 'params' in action
    if action['type'] == 'explore_area':
        assert 'position' in action['params']
        assert 'radius' in action['params']
    else:
        assert 'radius' in action['params']
        assert 'avoid_dangers' in action['params']

def test_weapon_selection(controller, game_state):
    """Teste la sélection d'arme"""
    # Ajout d'une deuxième arme
    game_state['inventory']['weapon2'] = {
        'id': 'weapon2',
        'category': 'weapon',
        'optimal_range': 50,
        'damage': 80,
        'ammo': 10
    }
    
    controller.ai_system.update(game_state)
    
    # Test à courte distance
    weapon_close = controller.ai_system._select_best_weapon(15.0)
    assert weapon_close['id'] == 'weapon1'  # L'arme avec la portée optimale de 20
    
    # Test à longue distance
    weapon_far = controller.ai_system._select_best_weapon(45.0)
    assert weapon_far['id'] == 'weapon2'  # L'arme avec la portée optimale de 50

def test_state_transitions(controller, game_state):
    """Teste les transitions d'état"""
    controller.toggle_ai_mode()
    
    # Test de transition normale
    assert controller.get_current_state()['ai_active'] == True
    
    # Test avec menace
    game_state['threats'] = [{
        'id': 'enemy1',
        'position': {'x': 10, 'y': 0, 'z': 0},
        'danger_level': 0.9
    }]
    controller.update(game_state, 0.1)
    
    # Test de désactivation
    controller.toggle_ai_mode()
    state = controller.get_current_state()
    assert state['ai_active'] == False
    assert state['transition_progress'] == 1.0

def test_ai_status_info(controller, game_state):
    """Teste les informations de statut de l'IA"""
    # En mode manuel
    status = controller.get_ai_status()
    assert status == {}
    
    # En mode IA
    controller.toggle_ai_mode()
    controller.update(game_state, 0.1)
    
    status = controller.get_ai_status()
    assert 'health' in status
    assert 'nearby_threats' in status
    assert 'known_locations' in status
    assert 'behavioral_profile' in status

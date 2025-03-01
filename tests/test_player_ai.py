"""
Tests pour le système d'IA du joueur
"""

import pytest
from src.player_ai.player_autonomous_system import PlayerAutonomousSystem, PlayerState, PlayerObjective
from src.player_ai.player_controller import PlayerController

def test_ai_toggle():
    """Teste l'activation/désactivation de l'IA"""
    system = PlayerAutonomousSystem()
    
    # Par défaut en mode manuel
    assert system.state == PlayerState.MANUAL
    
    # Active l'IA
    assert system.toggle_ai_control() == True
    assert system.state == PlayerState.AI_CONTROLLED
    
    # Désactive l'IA
    assert system.toggle_ai_control() == False
    assert system.state == PlayerState.MANUAL

def test_threat_evaluation():
    """Teste l'évaluation des menaces"""
    system = PlayerAutonomousSystem()
    
    # Situation sans menace
    game_state = {
        'health': 100,
        'position': {'x': 0, 'y': 0, 'z': 0},
        'threats': []
    }
    system._update_context(game_state)
    assert system._evaluate_threat_level() == 0.0
    
    # Situation avec menace proche
    game_state['threats'] = [{
        'position': {'x': 10, 'y': 0, 'z': 0},
        'danger_level': 0.8
    }]
    system._update_context(game_state)
    threat_level = system._evaluate_threat_level()
    assert threat_level > 0.0
    assert threat_level <= 1.0

def test_objective_determination():
    """Teste la détermination des objectifs"""
    system = PlayerAutonomousSystem()
    
    # Situation critique (santé basse)
    game_state = {
        'health': 30,
        'position': {'x': 0, 'y': 0, 'z': 0},
        'threats': []
    }
    system._update_context(game_state)
    objectives = system._determine_objectives()
    assert objectives[0][0] == PlayerObjective.HEAL
    
    # Situation de combat
    game_state = {
        'health': 80,
        'position': {'x': 0, 'y': 0, 'z': 0},
        'threats': [{
            'position': {'x': 20, 'y': 0, 'z': 0},
            'danger_level': 0.7
        }]
    }
    system._update_context(game_state)
    objectives = system._determine_objectives()
    assert PlayerObjective.COMBAT in [obj[0] for obj in objectives]

def test_action_planning():
    """Teste la planification des actions"""
    system = PlayerAutonomousSystem()
    
    # Test de soin
    game_state = {
        'health': 30,
        'position': {'x': 0, 'y': 0, 'z': 0},
        'inventory': {
            'medkit1': {'id': 'medkit1', 'type': 'medkit'}
        }
    }
    system._update_context(game_state)
    action = system._plan_healing_action()
    assert action['type'] == 'use_item'
    assert action['params']['item_id'] == 'medkit1'
    
    # Test de combat
    game_state = {
        'health': 80,
        'position': {'x': 0, 'y': 0, 'z': 0},
        'threats': [{
            'id': 'enemy1',
            'position': {'x': 20, 'y': 0, 'z': 0},
            'danger_level': 0.7
        }],
        'inventory': {
            'weapon1': {
                'id': 'weapon1',
                'category': 'weapon',
                'optimal_range': 15,
                'damage': 50,
                'ammo': 30
            }
        }
    }
    system._update_context(game_state)
    action = system._plan_combat_action(0.7)
    assert action['type'] in ['move_to', 'attack']

def test_controller_integration():
    """Teste l'intégration du contrôleur"""
    controller = PlayerController()
    
    # Test de basculement
    assert controller.toggle_ai_mode() == True
    assert controller.get_current_state()['ai_active'] == True
    
    # Test de mise à jour
    game_state = {
        'health': 100,
        'position': {'x': 0, 'y': 0, 'z': 0},
        'threats': []
    }
    action = controller.update(game_state, 0.1)
    assert action is not None
    
    # Test de désactivation
    assert controller.toggle_ai_mode() == False
    assert controller.get_current_state()['ai_active'] == False
    action = controller.update(game_state, 0.1)
    assert action is None

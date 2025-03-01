"""
Suite de tests unifiée pour le système NPC amélioré de STALKER 2
Ce module combine tous les tests en une suite cohérente et organisée.
"""

import pytest
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from unittest.mock import Mock, patch, MagicMock

# Import du système unifié
from src.npc.npc_unified_system import (
    UnifiedNPCSystem, NPCState, NPCStateType, 
    EmotionType, RelationType, Quest
)

# Configuration des tests
@pytest.fixture
def test_data_path():
    return Path(__file__).parent / 'data'

@pytest.fixture
def npc_system():
    return UnifiedNPCSystem()

@pytest.fixture
def mock_game_state():
    return {
        'health': 70,
        'in_combat': False,
        'inventory': [{'type': 'medkit', 'count': 1}],
        'threats': [],
        'radiation_level': 0.0,
        'time': datetime.now().isoformat()
    }

# Tests du système NPC unifié
class TestUnifiedNPCSystem:
    def test_npc_creation(self, npc_system):
        """Teste la création d'un nouveau PNJ"""
        npc_data = {
            'position': {'x': 100, 'y': 0, 'z': 100},
            'faction': 'stalkers',
            'personality_traits': {
                'aggression': 0.7,
                'courage': 0.8
            }
        }
        npc_id = npc_system.create_npc(npc_data)
        assert npc_id in npc_system.npcs
        assert npc_system.npcs[npc_id].faction == 'stalkers'
        assert npc_system.npcs[npc_id].personality_traits['aggression'] == 0.7

    def test_emotional_state_update(self, npc_system):
        """Teste la mise à jour de l'état émotionnel"""
        npc_data = {
            'position': {'x': 0, 'y': 0, 'z': 0},
            'personality_traits': {'aggression': 0.5}
        }
        npc_id = npc_system.create_npc(npc_data)
        
        game_state = {
            'threats': [{'position': {'x': 10, 'y': 0, 'z': 0}, 'level': 0.8}],
            'radiation_level': 0.3
        }
        
        npc_system.update_npc(npc_id, game_state)
        npc = npc_system.npcs[npc_id]
        assert npc.emotional_state['fear'] > 0

    def test_relationship_update(self, npc_system):
        """Teste la mise à jour des relations"""
        npc1_id = npc_system.create_npc({'position': {'x': 0, 'y': 0, 'z': 0}})
        npc2_id = npc_system.create_npc({'position': {'x': 5, 'y': 0, 'z': 0}})
        
        game_state = {
            'recent_interactions': [{
                'type': 'help',
                'target_id': npc2_id
            }]
        }
        
        npc_system.update_npc(npc1_id, game_state)
        npc1 = npc_system.npcs[npc1_id]
        assert npc1.relationships.get(npc2_id, 0) > 0

    def test_combat_behavior(self, npc_system):
        """Teste le comportement en combat"""
        npc_id = npc_system.create_npc({
            'position': {'x': 0, 'y': 0, 'z': 0},
            'personality_traits': {'aggression': 0.8},
            'health': 100
        })
        
        game_state = {
            'health': 90,
            'in_combat': True,
            'threats': [{'position': {'x': 10, 'y': 0, 'z': 0}, 'level': 0.7}]
        }
        
        npc_system.update_npc(npc_id, game_state)
        npc = npc_system.npcs[npc_id]
        
        # Vérification de l'état émotionnel en combat
        assert npc.emotional_state['anger'] > 0
        assert npc.state_type == NPCStateType.COMBAT

    def test_healing_behavior(self, npc_system):
        """Teste le comportement de guérison"""
        npc_id = npc_system.create_npc({
            'position': {'x': 0, 'y': 0, 'z': 0},
            'health': 30,
            'inventory': [{'type': 'medkit', 'count': 1}]
        })
        
        game_state = {
            'health': 30,
            'in_combat': False,
            'inventory': [{'type': 'medkit', 'count': 1}]
        }
        
        npc_system.update_npc(npc_id, game_state)
        npc = npc_system.npcs[npc_id]
        assert npc.state_type in [NPCStateType.IDLE, NPCStateType.RESTING]

    def test_quest_processing(self, npc_system):
        """Teste le traitement des quêtes"""
        npc_id = npc_system.create_npc({'position': {'x': 0, 'y': 0, 'z': 0}})
        quest = Quest(
            id='test_quest',
            title='Test Quest',
            description='Test quest description',
            objectives=[{
                'type': 'explore',
                'location': {'position': {'x': 10, 'y': 0, 'z': 0}, 'radius': 5.0},
                'status': 'active'
            }],
            rewards={'items': {'medkit': 1}}
        )
        
        npc = npc_system.npcs[npc_id]
        npc.current_quest = 'test_quest'
        npc_system.quests['test_quest'] = quest
        
        game_state = {
            'position': {'x': 10, 'y': 0, 'z': 0}
        }
        
        npc_system.update_npc(npc_id, game_state)
        assert npc_system.quests['test_quest'].objectives[0]['status'] == 'completed'

def test_save_load_state(npc_system, tmp_path):
    """Teste la sauvegarde et le chargement de l'état du système"""
    # Création d'un état initial
    npc_id = npc_system.create_npc({
        'position': {'x': 100, 'y': 0, 'z': 100},
        'faction': 'stalkers',
        'personality_traits': {'aggression': 0.7}
    })
    
    save_path = tmp_path / "test_save.json"
    
    # Sauvegarde
    npc_system.save_state(str(save_path))
    
    # Création d'un nouveau système et chargement
    new_system = UnifiedNPCSystem()
    new_system.load_state(str(save_path))
    
    # Vérification
    assert npc_id in new_system.npcs
    assert new_system.npcs[npc_id].faction == 'stalkers'
    assert new_system.npcs[npc_id].personality_traits['aggression'] == 0.7

def test_memory_system(npc_system):
    """Teste le système de mémoire"""
    npc_id = npc_system.create_npc({'position': {'x': 0, 'y': 0, 'z': 0}})
    
    # Création d'événements significatifs
    game_state = {
        'significant_events': [
            {'type': 'combat', 'description': 'Combat avec un mutant'},
            {'type': 'discovery', 'description': 'Découverte d\'un artefact'}
        ]
    }
    
    npc_system.update_npc(npc_id, game_state)
    npc = npc_system.npcs[npc_id]
    
    # Vérification de la mémoire
    assert len(npc.memory) > 0
    latest_memory = npc.memory[-1]
    assert 'significant_events' in latest_memory
    assert len(latest_memory['significant_events']) == 2

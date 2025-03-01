"""
Tests pour le système de logging de l'IA
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from src.logs.ai_logger import AILogger

@pytest.fixture
def logger(tmp_path):
    """Fixture pour créer un logger de test"""
    return AILogger(str(tmp_path))

def test_logger_initialization(tmp_path):
    """Test l'initialisation du logger"""
    logger = AILogger(str(tmp_path))
    assert (tmp_path / "ai_general.log").exists()
    assert (tmp_path / "ai_decisions.log").exists()
    assert (tmp_path / "ai_combat.log").exists()
    assert (tmp_path / "ai_state.log").exists()

def test_log_decision(logger):
    """Test l'enregistrement des décisions"""
    context = {"health": 100, "position": {"x": 0, "y": 0}}
    decision = {"type": "move", "target": {"x": 10, "y": 10}}
    
    logger.log_decision(
        context=context,
        decision_type="movement",
        decision_details=decision,
        confidence=0.8
    )
    
    log_file = Path(logger.log_dir) / "ai_decisions.log"
    with open(log_file, 'r', encoding='utf-8') as f:
        log_content = f.read()
        assert "movement" in log_content
        assert '"confidence": 0.8' in log_content
        assert '"health": 100' in log_content

def test_log_combat(logger):
    """Test l'enregistrement des actions de combat"""
    threat = {"id": "enemy1", "position": {"x": 10, "y": 0}}
    action = {"type": "attack", "weapon": "rifle1"}
    player_state = {"health": 80, "ammo": 30}
    
    logger.log_combat(
        threat=threat,
        action=action,
        player_state=player_state
    )
    
    log_file = Path(logger.log_dir) / "ai_combat.log"
    with open(log_file, 'r', encoding='utf-8') as f:
        log_content = f.read()
        assert "enemy1" in log_content
        assert "rifle1" in log_content
        assert '"health": 80' in log_content

def test_log_state_change(logger):
    """Test l'enregistrement des changements d'état"""
    old_state = {"mode": "exploration", "health": 100}
    new_state = {"mode": "combat", "health": 90}
    
    logger.log_state_change(
        old_state=old_state,
        new_state=new_state,
        trigger="enemy_spotted"
    )
    
    log_file = Path(logger.log_dir) / "ai_state.log"
    with open(log_file, 'r', encoding='utf-8') as f:
        log_content = f.read()
        assert "exploration" in log_content
        assert "combat" in log_content
        assert "enemy_spotted" in log_content

def test_log_error(logger):
    """Test l'enregistrement des erreurs"""
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.log_error(e, {"state": "testing"})
    
    log_file = Path(logger.log_dir) / "ai_general.log"
    with open(log_file, 'r', encoding='utf-8') as f:
        log_content = f.read()
        assert "ValueError" in log_content
        assert "Test error" in log_content

def test_create_session_log(logger):
    """Test la création d'un fichier de log de session"""
    session_file = logger.create_session_log()
    assert session_file.exists()
    assert "session_" in session_file.name

def test_archive_old_logs(logger, tmp_path):
    """Test l'archivage des anciens logs"""
    # Créer un vieux fichier de log
    old_log = tmp_path / "old_test.log"
    old_log.touch()
    
    logger.archive_old_logs(days_to_keep=0)
    
    archive_dir = tmp_path / "archive"
    assert archive_dir.exists()
    assert len(list(archive_dir.glob("*.log"))) > 0

def test_get_session_summary(logger):
    """Test la génération du résumé de session"""
    session_file = logger.create_session_log()
    
    # Générer quelques logs
    logger.log_decision({}, "test", {})
    logger.log_combat({}, {}, {})
    logger.log_state_change({}, {})
    
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.log_error(e, {})
    
    summary = logger.get_session_summary(session_file)
    
    assert summary["total_decisions"] >= 1
    assert summary["combat_actions"] >= 1
    assert summary["state_changes"] >= 1
    assert summary["errors"] >= 1
    assert summary["start_time"] is not None
    assert summary["end_time"] is not None

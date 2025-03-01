"""
Enhanced NPC Autonomous (ENA) System
==================================

Un système avancé d'IA pour les PNJ de jeux AAA.
"""

__version__ = "1.0.0"
__author__ = "Codeium AI"

from .core import *
from .games import *
from .utils import *

# Configuration par défaut
DEFAULT_CONFIG = {
    "ai_update_rate": 0.1,
    "behavior_update_rate": 0.05,
    "quest_update_rate": 1.0,
    "debug_mode": False
}

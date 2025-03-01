import os
import json
from typing import Dict, Any, Optional
from .logger import Logger

class Config:
    """Gestionnaire de configuration pour le système ENA."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = Logger("Config")
        self.config_path = config_path or "config/ena_config.json"
        self.config = self._load_default_config()
        
        if os.path.exists(self.config_path):
            self._load_config()
            
    def _load_default_config(self) -> Dict[str, Any]:
        """Charge la configuration par défaut."""
        return {
            "version": "1.0.0",
            "debug": False,
            "logging": {
                "level": "INFO",
                "file": "logs/ena.log",
                "max_size": 10485760,  # 10 MB
                "backup_count": 5
            },
            "ai": {
                "update_rate": 0.1,
                "max_npcs": 1000,
                "behavior_weights": {
                    "idle": 1.0,
                    "wander": 0.8,
                    "interact": 1.2,
                    "combat": 1.5,
                    "flee": 2.0
                },
                "perception_range": 50.0,
                "memory_duration": 300.0
            },
            "world": {
                "update_rate": 0.2,
                "max_regions": 100,
                "max_events": 50,
                "weather_change_probability": 0.001,
                "resource_regeneration_rate": 0.1
            },
            "quests": {
                "max_active_quests": 10,
                "quest_update_rate": 1.0,
                "reward_multiplier": 1.0
            },
            "factions": {
                "max_factions": 20,
                "relation_update_rate": 0.5,
                "influence_decay_rate": 0.1
            },
            "performance": {
                "threading": {
                    "enabled": True,
                    "max_threads": 4
                },
                "caching": {
                    "enabled": True,
                    "max_size": 1000
                },
                "optimization": {
                    "batch_updates": True,
                    "spatial_indexing": True
                }
            },
            "integration": {
                "stalker2": {
                    "enabled": True,
                    "scripts_path": "gamedata/scripts/ena",
                    "config_path": "gamedata/configs/ena"
                },
                "cyberpunk2077": {
                    "enabled": True,
                    "scripts_path": "r6/scripts/ena",
                    "config_path": "r6/config/ena"
                },
                "starfield": {
                    "enabled": True,
                    "scripts_path": "Data/Scripts/Source/ena",
                    "config_path": "Data/ena"
                }
            }
        }
        
    def _load_config(self):
        """Charge la configuration depuis le fichier."""
        try:
            with open(self.config_path, 'r') as f:
                user_config = json.load(f)
                
            # Fusion avec la configuration par défaut
            self._merge_configs(self.config, user_config)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la configuration: {str(e)}")
            
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]):
        """Fusionne la configuration utilisateur avec les valeurs par défaut."""
        for key, value in user.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_configs(default[key], value)
                else:
                    default[key] = value
                    
    def save(self):
        """Sauvegarde la configuration actuelle."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de la configuration: {str(e)}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration."""
        try:
            value = self.config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key: str, value: Any):
        """Définit une valeur de configuration."""
        try:
            keys = key.split('.')
            current = self.config
            
            # Navigation jusqu'au dernier niveau
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
                
            # Définition de la valeur
            current[keys[-1]] = value
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la définition de la configuration: {str(e)}")
            
    def validate(self) -> bool:
        """Valide la configuration actuelle."""
        try:
            # Vérification des valeurs requises
            required_keys = [
                "version",
                "ai.update_rate",
                "world.update_rate",
                "quests.quest_update_rate"
            ]
            
            for key in required_keys:
                if self.get(key) is None:
                    self.logger.error(f"Configuration invalide: {key} manquant")
                    return False
                    
            # Vérification des valeurs numériques
            numeric_ranges = {
                "ai.update_rate": (0.01, 1.0),
                "ai.max_npcs": (1, 10000),
                "world.update_rate": (0.01, 1.0),
                "world.max_regions": (1, 1000),
                "quests.max_active_quests": (1, 100)
            }
            
            for key, (min_val, max_val) in numeric_ranges.items():
                value = self.get(key)
                if value is not None:
                    if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                        self.logger.error(f"Configuration invalide: {key} doit être entre {min_val} et {max_val}")
                        return False
                        
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la validation de la configuration: {str(e)}")
            return False

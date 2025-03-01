from typing import Dict, Any, List, Optional
import numpy as np
from ..utils.logger import Logger
from ..utils.config import Config

class WorldManager:
    """Gestionnaire du monde et de l'environnement."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = Logger("WorldManager")
        self.regions = {}
        self.events = {}
        self.resources = {}
        self.weather = {}
        self.time = 0.0
        self.npcs = {}
        
    def register_region(self, region_id: str, region_data: Dict[str, Any]) -> bool:
        """Enregistre une nouvelle région."""
        try:
            self.regions[region_id] = {
                "data": region_data,
                "state": self._initialize_region_state(region_data),
                "events": [],
                "resources": {},
                "npcs": []
            }
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement de la région {region_id}: {str(e)}")
            return False
            
    def update(self, delta_time: float):
        """Met à jour l'état du monde."""
        try:
            # Mise à jour du temps
            self.time += delta_time
            
            # Mise à jour des régions
            for region_id, region in self.regions.items():
                self._update_region(region_id, region, delta_time)
                
            # Mise à jour des PNJ
            for npc_id, npc in self.npcs.items():
                self._update_npc(npc_id, npc, delta_time)
                
            # Mise à jour des événements
            self._update_events(delta_time)
                
            # Mise à jour des ressources
            self._update_resources(delta_time)
                
            # Mise à jour de la météo
            self._update_weather(delta_time)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du monde: {str(e)}")
            
    def get_region_state(self, region_id: str) -> Dict[str, Any]:
        """Récupère l'état d'une région."""
        return self.regions.get(region_id, {}).get("state", {})
        
    def spawn_event(self, event_type: str, region_id: str, event_data: Dict[str, Any]) -> str:
        """Crée un nouvel événement dans une région."""
        try:
            event_id = f"{event_type}_{len(self.events)}"
            
            event = {
                "type": event_type,
                "region": region_id,
                "data": event_data,
                "state": self._initialize_event_state(event_data),
                "time": self.time
            }
            
            self.events[event_id] = event
            self.regions[region_id]["events"].append(event_id)
            
            return event_id
        except Exception as e:
            self.logger.error(f"Erreur lors de la création de l'événement: {str(e)}")
            return None
            
    def handle_npc_spawn(self, event: Any) -> None:
        """Gère l'apparition d'un PNJ"""
        try:
            npc_data = event.data
            npc_id = npc_data.get("id")
            region_id = npc_data.get("region_id")
            
            if not npc_id or not region_id:
                self.logger.error("Données de PNJ invalides")
                return
                
            if region_id not in self.regions:
                self.logger.error(f"Région non trouvée: {region_id}")
                return
                
            self.npcs[npc_id] = {
                "region_id": region_id,
                "position": npc_data.get("position", [0, 0, 0]),
                "rotation": npc_data.get("rotation", [0, 0, 0]),
                "state": "idle"
            }
            
            self.logger.info(f"PNJ apparu: {npc_id} dans la région {region_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'apparition du PNJ: {str(e)}")
            
    def _initialize_region_state(self, region_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialise l'état d'une région."""
        return {
            "population": region_data.get("initial_population", 0),
            "danger_level": region_data.get("initial_danger", 0.0),
            "resources": region_data.get("initial_resources", {}),
            "faction_control": region_data.get("initial_control", {}),
            "weather": "clear",
            "time_of_day": 0.0,
            "events": [],
            "active_threats": [],
            "environment": {
                "temperature": region_data.get("base_temperature", 20.0),
                "humidity": region_data.get("base_humidity", 0.5),
                "radiation": region_data.get("base_radiation", 0.0),
                "toxicity": region_data.get("base_toxicity", 0.0)
            }
        }
        
    def _initialize_event_state(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialise l'état d'un événement."""
        return {
            "active": True,
            "progress": 0.0,
            "intensity": event_data.get("initial_intensity", 1.0),
            "duration": event_data.get("duration", 300.0),
            "affected_npcs": [],
            "effects": event_data.get("effects", {}),
            "rewards": event_data.get("rewards", {})
        }
        
    def _update_region(self, region_id: str, region: Dict[str, Any], delta_time: float) -> None:
        """Met à jour une région"""
        try:
            state = region["state"]
            
            # Mise à jour de l'environnement
            self._update_environment(state, delta_time)
            
            # Mise à jour de la population
            self._update_population(state, delta_time)
            
            # Mise à jour des ressources
            self._update_region_resources(state, delta_time)
            
            # Mise à jour du contrôle des factions
            self._update_faction_control(state, delta_time)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de la région: {str(e)}")
            
    def _update_npc(self, npc_id: str, npc: Dict[str, Any], delta_time: float) -> None:
        """Met à jour un PNJ"""
        try:
            # TODO: Implémenter la mise à jour des PNJ
            pass
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du PNJ: {str(e)}")
            
    def _update_events(self, delta_time: float) -> None:
        """Met à jour les événements"""
        try:
            # Mise à jour des événements actifs
            completed_events = []
            
            for event_id, event in self.events.items():
                if event["state"]["active"]:
                    try:
                        # Mise à jour de la progression
                        progress = event["state"]["progress"]
                        duration = event["state"]["duration"]
                        
                        progress += delta_time / duration
                        event["state"]["progress"] = progress
                        
                        # Vérification de la fin de l'événement
                        if progress >= 1.0:
                            event["state"]["active"] = False
                            completed_events.append(event_id)
                            
                        # Mise à jour de l'intensité
                        intensity = event["state"]["intensity"]
                        intensity *= (1.0 - progress)
                        event["state"]["intensity"] = intensity
                        
                    except Exception as e:
                        self.logger.error(f"Erreur lors de la mise à jour de l'événement: {str(e)}")
                        
            # Nettoyage des événements terminés
            for event_id in completed_events:
                self._cleanup_event(event_id)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour des événements: {str(e)}")
            
    def _update_resources(self, delta_time: float) -> None:
        """Met à jour les ressources"""
        try:
            # Mise à jour des ressources globales
            for resource_id, resource in self.resources.items():
                try:
                    # Mise à jour de la quantité
                    amount = resource["amount"]
                    regen_rate = resource.get("regeneration_rate", 0.0)
                    
                    amount += regen_rate * delta_time
                    resource["amount"] = max(0, min(amount, resource.get("max_amount", float("inf"))))
                    
                except Exception as e:
                    self.logger.error(f"Erreur lors de la mise à jour de la ressource: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour des ressources: {str(e)}")
            
    def _update_weather(self, delta_time: float) -> None:
        """Met à jour la météo"""
        try:
            # Mise à jour des conditions météorologiques
            for region_id, region in self.regions.items():
                try:
                    state = region["state"]
                    current_weather = state["weather"]
                    
                    # Probabilité de changement météo
                    if np.random.random() < 0.001 * delta_time:
                        # Sélection du nouveau temps
                        weather_types = ["clear", "cloudy", "rain", "storm"]
                        weights = [0.4, 0.3, 0.2, 0.1]
                        
                        new_weather = np.random.choice(weather_types, p=weights)
                        state["weather"] = new_weather
                        
                    # Mise à jour du temps de la journée
                    state["time_of_day"] = (state["time_of_day"] + delta_time / 86400.0) % 1.0
                    
                except Exception as e:
                    self.logger.error(f"Erreur lors de la mise à jour de la météo de la région: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de la météo: {str(e)}")
            
    def _update_environment(self, state: Dict[str, Any], delta_time: float):
        """Met à jour l'environnement d'une région."""
        env = state["environment"]
        
        # Variations naturelles
        env["temperature"] += np.random.normal(0, 0.1) * delta_time
        env["humidity"] += np.random.normal(0, 0.05) * delta_time
        
        # Application des effets des événements
        for event_id in state["events"]:
            if event_id in self.events:
                event = self.events[event_id]
                effects = event["state"]["effects"]
                
                if "temperature" in effects:
                    env["temperature"] += effects["temperature"] * delta_time
                if "radiation" in effects:
                    env["radiation"] += effects["radiation"] * delta_time
                    
        # Normalisation des valeurs
        env["temperature"] = np.clip(env["temperature"], -50, 50)
        env["humidity"] = np.clip(env["humidity"], 0, 1)
        env["radiation"] = np.clip(env["radiation"], 0, 100)
        env["toxicity"] = np.clip(env["toxicity"], 0, 100)
        
    def _update_population(self, state: Dict[str, Any], delta_time: float):
        """Met à jour la population d'une région."""
        # Facteurs affectant la population
        danger_factor = 1.0 - (state["danger_level"] / 100.0)
        resource_factor = min(1.0, sum(state["resources"].values()) / 100.0)
        
        # Croissance/décroissance naturelle
        growth_rate = 0.001 * danger_factor * resource_factor
        state["population"] += state["population"] * growth_rate * delta_time
        
        # Arrondi à l'entier le plus proche
        state["population"] = round(state["population"])
        
    def _update_region_resources(self, state: Dict[str, Any], delta_time: float):
        """Met à jour les ressources d'une région."""
        for resource, amount in state["resources"].items():
            # Consommation naturelle
            consumption_rate = 0.01 * state["population"]
            amount -= consumption_rate * delta_time
            
            # Régénération naturelle
            if amount < 100:
                regen_rate = 0.05 * (1.0 - amount / 100.0)
                amount += regen_rate * delta_time
                
            state["resources"][resource] = max(0, amount)
            
    def _update_faction_control(self, state: Dict[str, Any], delta_time: float):
        """Met à jour le contrôle des factions dans une région."""
        total_control = sum(state["faction_control"].values())
        
        if total_control > 0:
            # Normalisation du contrôle
            for faction in state["faction_control"]:
                state["faction_control"][faction] /= total_control
                
            # Lutte d'influence
            for faction, control in state["faction_control"].items():
                # Influence des autres factions
                other_factions = sum(c for f, c in state["faction_control"].items() if f != faction)
                
                # Changement de contrôle
                change_rate = 0.1 * (other_factions - control)
                state["faction_control"][faction] += change_rate * delta_time
                
    def _cleanup_event(self, event_id: str):
        """Nettoie un événement terminé."""
        if event_id in self.events:
            event = self.events[event_id]
            region_id = event["region"]
            
            if region_id in self.regions:
                # Retrait de l'événement de la région
                self.regions[region_id]["events"].remove(event_id)
                
            # Distribution des récompenses
            rewards = event["state"].get("rewards", {})
            if rewards:
                self._distribute_rewards(rewards, event["state"]["affected_npcs"])
                
    def _distribute_rewards(self, rewards: Dict[str, Any], affected_npcs: List[str]):
        """Distribue les récompenses d'un événement."""
        if not affected_npcs:
            return
            
        # Distribution équitable entre les PNJ affectés
        share = 1.0 / len(affected_npcs)
        
        for npc_id in affected_npcs:
            try:
                # Application des récompenses
                for reward_type, amount in rewards.items():
                    if reward_type == "experience":
                        # TODO: Ajouter l'expérience au PNJ
                        pass
                    elif reward_type == "resources":
                        # TODO: Ajouter les ressources au PNJ
                        pass
                    elif reward_type == "reputation":
                        # TODO: Modifier la réputation du PNJ
                        pass
                        
            except Exception as e:
                self.logger.error(f"Erreur lors de la distribution des récompenses au PNJ: {str(e)}")

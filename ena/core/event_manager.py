"""
Gestionnaire d'événements pour ENA
"""
from typing import Dict, Any, List, Callable, Optional
from ..utils.logger import Logger

class Event:
    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.type = event_type
        self.data = data

class EventManager:
    def __init__(self):
        self.logger = Logger("EventManager")
        self.listeners: Dict[str, List[Callable[[Event], None]]] = {}
        
    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """Ajoute un écouteur d'événements"""
        try:
            if event_type not in self.listeners:
                self.listeners[event_type] = []
            self.listeners[event_type].append(callback)
            self.logger.debug(f"Écouteur ajouté pour l'événement: {event_type}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout de l'écouteur: {str(e)}")
            
    def unsubscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """Retire un écouteur d'événements"""
        try:
            if event_type in self.listeners:
                self.listeners[event_type].remove(callback)
                self.logger.debug(f"Écouteur retiré pour l'événement: {event_type}")
        except Exception as e:
            self.logger.error(f"Erreur lors du retrait de l'écouteur: {str(e)}")
            
    def emit(self, event: Event) -> None:
        """Émet un événement"""
        try:
            if event.type in self.listeners:
                for callback in self.listeners[event.type]:
                    try:
                        callback(event)
                    except Exception as e:
                        self.logger.error(f"Erreur dans l'écouteur: {str(e)}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'émission de l'événement: {str(e)}")
            
    def emit_all(self, events: List[Event]) -> None:
        """Émet plusieurs événements"""
        for event in events:
            self.emit(event)
            
    def clear_listeners(self, event_type: Optional[str] = None) -> None:
        """Efface les écouteurs"""
        try:
            if event_type:
                if event_type in self.listeners:
                    self.listeners[event_type].clear()
                    self.logger.debug(f"Écouteurs effacés pour l'événement: {event_type}")
            else:
                self.listeners.clear()
                self.logger.debug("Tous les écouteurs ont été effacés")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'effacement des écouteurs: {str(e)}")
            
    def get_listener_count(self, event_type: str) -> int:
        """Retourne le nombre d'écouteurs pour un type d'événement"""
        return len(self.listeners.get(event_type, []))

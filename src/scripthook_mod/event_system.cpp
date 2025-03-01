#include "event_system.h"
#include "natives.h"

void EventSystem::registerCallback(GameEvent event, EventCallback callback) {
    listeners.push_back({event, callback});
}

void EventSystem::triggerEvent(const EventData& eventData) {
    eventQueue.push_back(eventData);
}

void EventSystem::update() {
    // Traiter tous les événements en attente
    for (const auto& eventData : eventQueue) {
        for (const auto& listener : listeners) {
            if (listener.event == eventData.type) {
                listener.callback(eventData);
            }
        }
    }
    eventQueue.clear();

    // Détecter automatiquement les événements du jeu
    Ped playerPed = PLAYER::PLAYER_PED_ID();
    Vector3 playerPos = ENTITY::GET_ENTITY_COORDS(playerPed, true);

    // Détecter les coups de feu
    if (WEAPON::HAS_PED_FIRED_GUN(playerPed, 1000)) {
        EventData eventData{
            GameEvent::GUNSHOT_HEARD,
            playerPed,
            0,
            playerPos,
            1.0f
        };
        triggerEvent(eventData);
    }

    // Détecter l'entrée/sortie de véhicule
    static bool wasInVehicle = false;
    bool isInVehicle = PED::IS_PED_IN_ANY_VEHICLE(playerPed, false);
    
    if (isInVehicle != wasInVehicle) {
        EventData eventData{
            isInVehicle ? GameEvent::PLAYER_ENTERED_VEHICLE : GameEvent::PLAYER_LEFT_VEHICLE,
            playerPed,
            0,
            playerPos,
            1.0f
        };
        triggerEvent(eventData);
        wasInVehicle = isInVehicle;
    }
}

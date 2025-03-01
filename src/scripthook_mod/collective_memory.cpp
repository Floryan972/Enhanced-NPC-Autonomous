#include "collective_memory.h"
#include "natives.h"
#include "social_group_system.h"
#include "personality_system.h"
#include "event_manager.h"

void CollectiveMemory::recordEvent(const std::string& groupId, const CollectiveMemoryEvent& event) {
    auto& memory = groupMemories[groupId];
    memory.events.push_back(event);

    // Mettre à jour les acteurs connus
    for (Ped ped : event.involvedPeds) {
        memory.knownActors[ped] = std::max(memory.knownActors[ped], event.importance);
    }

    // Ajouter le lieu si important
    if (event.importance > 0.7f) {
        memory.significantLocations.push_back(event.location);
    }

    // Propager la mémoire aux groupes alliés
    propagateMemory(event);
    
    // Mettre à jour la tension du groupe
    updateGroupTension(groupId);
}

void CollectiveMemory::updateMemories() {
    float currentTime = MISC::GET_GAME_TIMER() / 1000.0f;

    for (auto& [groupId, memory] : groupMemories) {
        // Mettre à jour l'importance des événements avec le temps
        for (auto& event : memory.events) {
            float timePassed = currentTime - event.timeStamp;
            event.importance *= std::max(0.0f, 1.0f - (timePassed / 3600.0f)); // Diminue sur une heure
        }

        // Nettoyer les événements non importants
        memory.events.erase(
            std::remove_if(
                memory.events.begin(),
                memory.events.end(),
                [](const CollectiveMemoryEvent& e) { return e.importance < 0.1f; }
            ),
            memory.events.end()
        );

        // Mettre à jour les comportements basés sur la météo
        updateWeatherBehavior(groupId);
    }
}

void CollectiveMemory::propagateMemory(const CollectiveMemoryEvent& event) {
    // Propager aux groupes proches
    const float PROPAGATION_RADIUS = 100.0f;
    
    for (auto& [targetGroupId, targetMemory] : groupMemories) {
        bool shouldPropagate = false;
        
        // Vérifier si un membre du groupe cible est proche
        for (const Vector3& loc : targetMemory.significantLocations) {
            float distance = SYSTEM::VDIST(
                event.location.x, event.location.y, event.location.z,
                loc.x, loc.y, loc.z
            );
            
            if (distance < PROPAGATION_RADIUS) {
                shouldPropagate = true;
                break;
            }
        }

        if (shouldPropagate) {
            CollectiveMemoryEvent propagatedEvent = event;
            propagatedEvent.importance *= 0.8f; // Réduire l'importance lors de la propagation
            targetMemory.events.push_back(propagatedEvent);
        }
    }
}

void CollectiveMemory::updateGroupTension(const std::string& groupId) {
    auto& memory = groupMemories[groupId];
    float tension = 0.0f;
    float currentTime = MISC::GET_GAME_TIMER() / 1000.0f;

    // Calculer la tension basée sur les événements récents
    for (const auto& event : memory.events) {
        float timeFactor = std::max(0.0f, 1.0f - ((currentTime - event.timeStamp) / 3600.0f));
        
        if (event.type == MemoryType::THREAT) {
            tension += event.importance * timeFactor * 2.0f;
        } else if (event.type == MemoryType::NEGATIVE) {
            tension += event.importance * timeFactor;
        } else if (event.type == MemoryType::POSITIVE) {
            tension -= event.importance * timeFactor * 0.5f;
        }
    }

    memory.groupTension = std::clamp(tension, 0.0f, 1.0f);

    // Déclencher des événements si la tension est trop élevée
    if (memory.groupTension > 0.8f) {
        EventManager::getInstance().triggerEvent(
            SpecialEventType::RIOT,
            memory.significantLocations[0],  // Utiliser le premier lieu significatif
            50.0f
        );
    }
}

void CollectiveMemory::recordWeatherEvent(const Vector3& location, const std::string& weatherType) {
    CollectiveMemoryEvent weatherEvent;
    weatherEvent.type = MemoryType::NEUTRAL;
    weatherEvent.location = location;
    weatherEvent.timeStamp = MISC::GET_GAME_TIMER() / 1000.0f;
    weatherEvent.description = weatherType;
    weatherEvent.importance = 0.7f;

    weatherEvents.push_back(weatherEvent);

    // Informer tous les groupes du changement météo
    for (auto& [groupId, memory] : groupMemories) {
        recordEvent(groupId, weatherEvent);
    }
}

bool CollectiveMemory::shouldReactToWeather(const std::string& groupId, const Vector3& location) {
    auto it = groupMemories.find(groupId);
    if (it == groupMemories.end()) return false;

    // Vérifier les événements météo récents dans la zone
    float currentTime = MISC::GET_GAME_TIMER() / 1000.0f;
    
    for (const auto& event : weatherEvents) {
        float timePassed = currentTime - event.timeStamp;
        if (timePassed < 300.0f) { // 5 minutes
            float distance = SYSTEM::VDIST(
                location.x, location.y, location.z,
                event.location.x, event.location.y, event.location.z
            );
            
            if (distance < 100.0f) {
                return true;
            }
        }
    }

    return false;
}

void CollectiveMemory::updateWeatherBehavior(const std::string& groupId) {
    auto& memory = groupMemories[groupId];
    
    // Obtenir la météo actuelle
    Hash weatherHash = MISC::GET_PREV_WEATHER_TYPE_HASH_NAME();
    
    // Adapter le comportement du groupe en fonction de la météo
    for (const auto& [ped, importance] : memory.knownActors) {
        if (!ENTITY::DOES_ENTITY_EXIST(ped)) continue;

        Vector3 pedPos = ENTITY::GET_ENTITY_COORDS(ped, true);
        
        if (MISC::IS_NEXT_WEATHER_TYPE("THUNDER") || MISC::IS_NEXT_WEATHER_TYPE("RAIN")) {
            // Chercher un abri
            bool foundShelter = false;
            for (const Vector3& loc : memory.significantLocations) {
                if (INTERIOR::IS_VALID_INTERIOR(INTERIOR::GET_INTERIOR_AT_COORDS(
                    loc.x, loc.y, loc.z))) {
                    AI::TASK_GO_TO_COORD_ANY_MEANS(
                        ped, loc.x, loc.y, loc.z,
                        2.0f, 0, 0, 786603, 0xbf800000
                    );
                    foundShelter = true;
                    break;
                }
            }

            // Si pas d'abri connu, utiliser une animation de protection
            if (!foundShelter) {
                AI::TASK_START_SCENARIO_IN_PLACE(ped, "WORLD_HUMAN_GUARD_STAND", 0, true);
            }
        }
    }
}

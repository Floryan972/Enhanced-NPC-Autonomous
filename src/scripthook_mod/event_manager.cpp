#include "event_manager.h"
#include "natives.h"
#include "personality_system.h"
#include "routine_system.h"
#include "social_group_system.h"

void EventManager::updateEvents() {
    float deltaTime = MISC::GET_FRAME_TIME();
    
    // Mettre à jour les événements actifs
    for (auto it = activeEvents.begin(); it != activeEvents.end();) {
        it->timeRemaining -= deltaTime;
        
        if (it->timeRemaining <= 0.0f) {
            it = activeEvents.erase(it);
        } else {
            handleEventEffects(*it);
            ++it;
        }
    }

    // Vérifier les déclencheurs d'événements
    for (const auto& [type, triggers] : eventTriggers) {
        for (const auto& trigger : triggers) {
            if (rand() % 100 < trigger.probability * 100 && trigger.condition()) {
                triggerEvent(type, trigger.location, trigger.radius);
            }
        }
    }
}

void EventManager::triggerEvent(SpecialEventType type, const Vector3& location, float radius) {
    ActiveEvent event;
    event.type = type;
    event.epicenter = location;
    event.radius = radius;
    event.intensity = 1.0f;
    event.isActive = true;

    // Configurer la durée en fonction du type d'événement
    switch (type) {
        case SpecialEventType::RIOT:
            event.duration = 300.0f;  // 5 minutes
            break;
        case SpecialEventType::GANG_WAR:
            event.duration = 600.0f;  // 10 minutes
            break;
        case SpecialEventType::CELEBRATION:
            event.duration = 900.0f;  // 15 minutes
            break;
        default:
            event.duration = 300.0f;
    }

    event.timeRemaining = event.duration;
    activeEvents.push_back(event);

    // Créer l'ambiance initiale
    createEventAmbience(event);
}

void EventManager::handleEventEffects(const ActiveEvent& event) {
    // Obtenir tous les NPCs dans la zone d'effet
    const int MAX_AFFECTED_PEDS = 50;
    Ped affectedPeds[MAX_AFFECTED_PEDS];
    int count = worldGetAllPeds(affectedPeds, MAX_AFFECTED_PEDS);

    for (int i = 0; i < count; i++) {
        Ped ped = affectedPeds[i];
        if (ENTITY::DOES_ENTITY_EXIST(ped) && !PED::IS_PED_A_PLAYER(ped)) {
            Vector3 pedPos = ENTITY::GET_ENTITY_COORDS(ped, true);
            float distance = SYSTEM::VDIST(
                pedPos.x, pedPos.y, pedPos.z,
                event.epicenter.x, event.epicenter.y, event.epicenter.z
            );

            if (distance < event.radius) {
                updateNPCBehavior(ped, event);
                
                // Interrompre les routines normales
                RoutineSystem::getInstance().interruptRoutine(ped);
            }
        }
    }

    // Maintenir les effets visuels et sonores
    createEventAmbience(event);
}

void EventManager::updateNPCBehavior(Ped ped, const ActiveEvent& event) {
    auto* personality = PersonalitySystem::getInstance().getPersonality(ped);
    if (!personality) return;

    switch (event.type) {
        case SpecialEventType::RIOT:
            if (personality->type == PersonalityType::AGGRESSIVE) {
                // Rejoindre l'émeute
                AI::TASK_COMBAT_HATED_TARGETS_IN_AREA(ped, 
                    event.epicenter.x, event.epicenter.y, event.epicenter.z, 
                    event.radius, 0);
            } else {
                // Fuir la zone
                AI::TASK_SMART_FLEE_COORD(ped,
                    event.epicenter.x, event.epicenter.y, event.epicenter.z,
                    event.radius * 1.5f, -1, false, false);
            }
            break;

        case SpecialEventType::CELEBRATION:
            // Animations de fête
            switch (rand() % 3) {
                case 0:
                    AI::TASK_START_SCENARIO_IN_PLACE(ped, "WORLD_HUMAN_CHEERING", 0, true);
                    break;
                case 1:
                    AI::TASK_START_SCENARIO_IN_PLACE(ped, "WORLD_HUMAN_DRINKING", 0, true);
                    break;
                case 2:
                    AI::TASK_START_SCENARIO_IN_PLACE(ped, "WORLD_HUMAN_PARTYING", 0, true);
                    break;
            }
            break;

        case SpecialEventType::EMERGENCY:
            if (personality->type == PersonalityType::PROTECTIVE) {
                // Aider les autres
                const int MAX_NEARBY = 5;
                Ped nearbyPeds[MAX_NEARBY];
                int count = worldGetAllPeds(nearbyPeds, MAX_NEARBY);
                
                for (int i = 0; i < count; i++) {
                    Ped nearbyPed = nearbyPeds[i];
                    if (PED::IS_PED_INJURED(nearbyPed)) {
                        AI::TASK_GOTO_ENTITY(ped, nearbyPed, -1, 0.0f, 2.0f, 0);
                        break;
                    }
                }
            } else {
                // Évacuer la zone
                AI::TASK_SMART_FLEE_COORD(ped,
                    event.epicenter.x, event.epicenter.y, event.epicenter.z,
                    event.radius, -1, false, false);
            }
            break;
    }
}

void EventManager::createEventAmbience(const ActiveEvent& event) {
    switch (event.type) {
        case SpecialEventType::RIOT:
            // Effets de fumée et de feu
            GRAPHICS::USE_PARTICLE_FX_ASSET("scr_trevor1");
            GRAPHICS::START_PARTICLE_FX_NON_LOOPED_AT_COORD(
                "scr_trev1_trailer_boosh",
                event.epicenter.x, event.epicenter.y, event.epicenter.z,
                0.0f, 0.0f, 0.0f, 1.0f, false, false, false
            );
            break;

        case SpecialEventType::CELEBRATION:
            // Effets de fête
            GRAPHICS::USE_PARTICLE_FX_ASSET("scr_rcpaparazzo1");
            GRAPHICS::START_PARTICLE_FX_NON_LOOPED_AT_COORD(
                "scr_mich4_firework_sparkle_spawn",
                event.epicenter.x, event.epicenter.y, event.epicenter.z + 20.0f,
                0.0f, 0.0f, 0.0f, 1.0f, false, false, false
            );
            break;

        case SpecialEventType::EMERGENCY:
            // Lumières d'urgence
            GRAPHICS::DRAW_LIGHT_WITH_RANGE(
                event.epicenter.x, event.epicenter.y, event.epicenter.z + 5.0f,
                255, 0, 0,  // Rouge
                event.radius,
                1.0f
            );
            break;
    }
}

void EventManager::spawnEventProps(const ActiveEvent& event) {
    // Spawn des objets appropriés pour l'événement
    switch (event.type) {
        case SpecialEventType::RIOT:
            // Spawn des barricades et des débris
            break;
        case SpecialEventType::CELEBRATION:
            // Spawn des décorations
            break;
        case SpecialEventType::EMERGENCY:
            // Spawn des véhicules d'urgence
            break;
    }
}

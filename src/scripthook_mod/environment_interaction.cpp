#include "environment_interaction.h"
#include "natives.h"
#include "social_group_system.h"
#include "collective_memory.h"
#include "group_learning.h"

void EnvironmentInteraction::discoverInteractionPoint(const Vector3& location, InteractionType type) {
    // Créer un nouveau point d'interaction
    InteractionPoint point;
    point.location = location;
    point.type = type;
    point.usefulness = 1.0f;
    point.timesUsed = 0;
    point.isOccupied = false;

    // Ajouter des comportements compatibles
    switch (type) {
        case InteractionType::HIDE:
            point.compatibleBehaviors = {"stealth", "escape", "ambush"};
            break;
        case InteractionType::OBSERVE:
            point.compatibleBehaviors = {"patrol", "surveillance", "hunting"};
            break;
        case InteractionType::GATHER:
            point.compatibleBehaviors = {"resource_collection", "scavenging"};
            break;
    }

    // Ajouter le point à toutes les zones environnantes
    float searchRadius = 100.0f;
    for (auto& [zoneId, data] : environmentData) {
        Vector3 zoneCenter;  // Calculer le centre de la zone
        float distance = SYSTEM::VDIST(
            location.x, location.y, location.z,
            zoneCenter.x, zoneCenter.y, zoneCenter.z
        );

        if (distance < searchRadius) {
            data.interactionPoints.push_back(point);
        }
    }
}

void EnvironmentInteraction::updateInteractionPoints() {
    for (auto& [zoneId, data] : environmentData) {
        for (auto& point : data.interactionPoints) {
            // Vérifier si le point est toujours valide
            if (!PATHFIND::GET_SAFE_COORD_FOR_PED(
                point.location.x, point.location.y, point.location.z,
                true, &point.location, 16
            )) {
                point.usefulness *= 0.8f;
                continue;
            }

            // Mettre à jour l'occupation
            const int MAX_NEARBY_PEDS = 5;
            Ped nearbyPeds[MAX_NEARBY_PEDS];
            int count = worldGetAllPeds(nearbyPeds, MAX_NEARBY_PEDS);
            
            point.isOccupied = false;
            for (int i = 0; i < count; i++) {
                Ped ped = nearbyPeds[i];
                if (!ENTITY::DOES_ENTITY_EXIST(ped)) continue;

                Vector3 pedPos = ENTITY::GET_ENTITY_COORDS(ped, true);
                float distance = SYSTEM::VDIST(
                    pedPos.x, pedPos.y, pedPos.z,
                    point.location.x, point.location.y, point.location.z
                );

                if (distance < 2.0f) {
                    point.isOccupied = true;
                    point.timesUsed++;
                    break;
                }
            }
        }

        // Nettoyer les points inutilisés
        data.interactionPoints.erase(
            std::remove_if(
                data.interactionPoints.begin(),
                data.interactionPoints.end(),
                [](const InteractionPoint& p) { return p.usefulness < 0.2f; }
            ),
            data.interactionPoints.end()
        );
    }
}

void EnvironmentInteraction::createEnvironmentalEvent(const Vector3& location, const std::string& eventType) {
    // Créer un événement environnemental
    CollectiveMemoryEvent envEvent;
    envEvent.location = location;
    envEvent.timeStamp = MISC::GET_GAME_TIMER() / 1000.0f;
    envEvent.importance = 0.8f;

    if (eventType == "natural_disaster") {
        // Déclencher un événement catastrophique
        EventManager::getInstance().triggerEvent(
            SpecialEventType::NATURAL_DISASTER,
            location,
            150.0f
        );

        // Mettre à jour les niveaux de danger
        for (auto& [zoneId, data] : environmentData) {
            Vector3 zoneCenter;  // Calculer le centre de la zone
            float distance = SYSTEM::VDIST(
                location.x, location.y, location.z,
                zoneCenter.x, zoneCenter.y, zoneCenter.z
            );

            if (distance < 200.0f) {
                data.environmentalThreat = std::min(data.environmentalThreat + 0.3f, 1.0f);
                data.dangerLevels[location] = 1.0f;
            }
        }
    }

    // Informer les groupes
    for (auto& [groupId, _] : SocialGroupSystem::getInstance().getGroups()) {
        CollectiveMemory::getInstance().recordEvent(groupId, envEvent);
        GroupLearning::getInstance().learnFromEvents(groupId, envEvent);
    }
}

void EnvironmentInteraction::modifyEnvironment(const Vector3& location, const std::string& modificationType) {
    if (modificationType == "create_cover") {
        // Créer un nouveau point de couverture
        InteractionPoint cover;
        cover.location = location;
        cover.type = InteractionType::HIDE;
        cover.usefulness = 1.0f;
        
        for (auto& [zoneId, data] : environmentData) {
            Vector3 zoneCenter;  // Calculer le centre de la zone
            float distance = SYSTEM::VDIST(
                location.x, location.y, location.z,
                zoneCenter.x, zoneCenter.y, zoneCenter.z
            );

            if (distance < 50.0f) {
                data.interactionPoints.push_back(cover);
            }
        }
    } else if (modificationType == "block_path") {
        // Bloquer un chemin
        PATHFIND::SET_ROADS_IN_AREA(
            location.x - 5.0f, location.y - 5.0f, location.z - 5.0f,
            location.x + 5.0f, location.y + 5.0f, location.z + 5.0f,
            false, true
        );
    }
}

void EnvironmentInteraction::synchronizeWithWeather() {
    Hash weather = MISC::GET_PREV_WEATHER_TYPE_HASH_NAME();
    
    for (auto& [zoneId, data] : environmentData) {
        // Adapter les points d'interaction selon la météo
        for (auto& point : data.interactionPoints) {
            if (weather == MISC::GET_HASH_KEY("RAIN") || 
                weather == MISC::GET_HASH_KEY("THUNDER")) {
                // Augmenter l'utilité des abris
                if (point.type == InteractionType::HIDE) {
                    point.usefulness *= 1.2f;
                }
            } else if (weather == MISC::GET_HASH_KEY("CLEAR")) {
                // Favoriser les points d'observation
                if (point.type == InteractionType::OBSERVE) {
                    point.usefulness *= 1.1f;
                }
            }
            
            point.usefulness = std::clamp(point.usefulness, 0.0f, 1.0f);
        }

        // Mettre à jour les niveaux de danger
        updateDangerLevels();
    }
}

InteractionPoint* EnvironmentInteraction::findBestInteractionPoint(
    const Vector3& location, InteractionType type) {
    
    InteractionPoint* bestPoint = nullptr;
    float bestScore = -1.0f;
    
    for (auto& [zoneId, data] : environmentData) {
        for (auto& point : data.interactionPoints) {
            if (point.type != type || point.isOccupied) continue;

            float distance = SYSTEM::VDIST(
                location.x, location.y, location.z,
                point.location.x, point.location.y, point.location.z
            );

            // Calculer un score basé sur la distance et l'utilité
            float score = point.usefulness * (1.0f - (distance / 200.0f));
            
            if (score > bestScore) {
                bestScore = score;
                bestPoint = &point;
            }
        }
    }
    
    return bestPoint;
}

void EnvironmentInteraction::updateDangerLevels() {
    for (auto& [zoneId, data] : environmentData) {
        // Réduire progressivement les niveaux de danger
        for (auto& [location, danger] : data.dangerLevels) {
            danger *= 0.95f;  // Diminution progressive
        }

        // Nettoyer les niveaux de danger insignifiants
        auto it = data.dangerLevels.begin();
        while (it != data.dangerLevels.end()) {
            if (it->second < 0.1f) {
                it = data.dangerLevels.erase(it);
            } else {
                ++it;
            }
        }

        // Mettre à jour la menace environnementale globale
        data.environmentalThreat *= 0.99f;
    }
}

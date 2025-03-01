#include "environmental_system.h"
#include "natives.h"
#include <algorithm>

void EnvironmentalSystem::updateEnvironment(const Vector3& position) {
    // Mettre à jour les points de couverture dans la zone
    scanForCoverPoints(position);
    
    // Vérifier le niveau de danger
    float dangerLevel = calculateDangerLevel(position);
    
    // Mettre à jour les points sûrs si le niveau de danger change
    if (dangerLevel > 0.7f) {
        Vector3 safe = findNearestSafeSpot(position);
        if (safe.x != 0.0f || safe.y != 0.0f || safe.z != 0.0f) {
            safeSpots.push_back(safe);
        }
    }
}

float EnvironmentalSystem::calculateDangerLevel(const Vector3& position) {
    float danger = 0.0f;
    
    // Vérifier les menaces à proximité
    const int MAX_THREATS = 20;
    Ped nearbyPeds[MAX_THREATS];
    int count = worldGetAllPeds(nearbyPeds, MAX_THREATS);
    
    for (int i = 0; i < count; i++) {
        Ped ped = nearbyPeds[i];
        if (ENTITY::DOES_ENTITY_EXIST(ped)) {
            // Vérifier si le PED est armé
            if (WEAPON::IS_PED_ARMED(ped, 7)) {
                danger += 0.2f;
            }
            
            // Vérifier si le PED est en combat
            if (PED::IS_PED_IN_COMBAT(ped, PLAYER::PLAYER_PED_ID())) {
                danger += 0.3f;
            }
        }
    }
    
    // Vérifier les explosions et incendies
    if (MISC::GET_NUMBER_OF_FIRES_IN_RANGE(position.x, position.y, position.z, 50.0f) > 0) {
        danger += 0.4f;
    }
    
    return std::min(danger, 1.0f);
}

void EnvironmentalSystem::scanForCoverPoints(const Vector3& center) {
    coverPoints.clear();
    
    // Rechercher des points de couverture dans un rayon
    float radius = 50.0f;
    float step = 5.0f;
    
    for (float x = -radius; x <= radius; x += step) {
        for (float y = -radius; y <= radius; y += step) {
            Vector3 testPos = {
                center.x + x,
                center.y + y,
                center.z
            };
            
            // Vérifier si la position peut servir de couverture
            if (MISC::GET_GROUND_Z_FOR_3D_COORD(testPos.x, testPos.y, testPos.z + 100.0f, &testPos.z, 0)) {
                if (PED::IS_PED_BEHIND_COVER(PLAYER::PLAYER_PED_ID(), testPos.x, testPos.y, testPos.z, true)) {
                    coverPoints.push_back(testPos);
                }
            }
        }
    }
}

Vector3 EnvironmentalSystem::findNearestSafeSpot(const Vector3& position) {
    Vector3 nearest = {0.0f, 0.0f, 0.0f};
    float minDistance = 999999.0f;
    
    // Vérifier les points de couverture existants
    for (const auto& point : coverPoints) {
        float distance = SYSTEM::VDIST(
            position.x, position.y, position.z,
            point.x, point.y, point.z
        );
        
        if (distance < minDistance && isPositionSafe(point)) {
            minDistance = distance;
            nearest = point;
        }
    }
    
    return nearest;
}

bool EnvironmentalSystem::isPositionSafe(const Vector3& position) {
    // Vérifier si la position est sûre
    if (calculateDangerLevel(position) > 0.3f) {
        return false;
    }
    
    // Vérifier si la position est accessible
    if (!PATHFIND::GET_SAFE_COORD_FOR_PED(
        position.x, position.y, position.z,
        true, &position, 16
    )) {
        return false;
    }
    
    return true;
}

void EnvironmentalSystem::handleWeatherEffects() {
    // Obtenir les conditions météorologiques actuelles
    int weather = MISC::GET_PREV_WEATHER_TYPE_HASH_NAME();
    
    // Ajuster le comportement des NPCs en fonction de la météo
    const int MAX_PEDS = 20;
    Ped peds[MAX_PEDS];
    int count = worldGetAllPeds(peds, MAX_PEDS);
    
    for (int i = 0; i < count; i++) {
        Ped ped = peds[i];
        if (ENTITY::DOES_ENTITY_EXIST(ped) && !PED::IS_PED_A_PLAYER(ped)) {
            // Réactions à la pluie
            if (MISC::IS_NEXT_WEATHER_TYPE("RAIN") || MISC::IS_NEXT_WEATHER_TYPE("THUNDER")) {
                // Chercher un abri
                Vector3 pedPos = ENTITY::GET_ENTITY_COORDS(ped, true);
                Vector3 shelter = findNearestSafeSpot(pedPos);
                
                if (shelter.x != 0.0f || shelter.y != 0.0f || shelter.z != 0.0f) {
                    AI::TASK_GO_TO_COORD_ANY_MEANS(
                        ped, shelter.x, shelter.y, shelter.z,
                        2.0f, 0, 0, 786603, 0xbf800000
                    );
                }
            }
        }
    }
}

void EnvironmentalSystem::updateCoverPoints() {
    // Mettre à jour périodiquement les points de couverture
    Vector3 playerPos = ENTITY::GET_ENTITY_COORDS(PLAYER::PLAYER_PED_ID(), true);
    scanForCoverPoints(playerPos);
    
    // Nettoyer les points de couverture invalides
    coverPoints.erase(
        std::remove_if(
            coverPoints.begin(),
            coverPoints.end(),
            [this](const Vector3& point) { return !isPositionSafe(point); }
        ),
        coverPoints.end()
    );
}

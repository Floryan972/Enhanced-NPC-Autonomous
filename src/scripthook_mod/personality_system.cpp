#include "personality_system.h"
#include "natives.h"
#include "event_system.h"
#include <cmath>

void PersonalitySystem::initializePersonality(Ped ped) {
    PersonalityTraits traits;
    
    // Génération aléatoire de personnalité
    int personalityRoll = rand() % 100;
    if (personalityRoll < 15) traits.type = PersonalityType::AGGRESSIVE;
    else if (personalityRoll < 35) traits.type = PersonalityType::CAUTIOUS;
    else if (personalityRoll < 50) traits.type = PersonalityType::FRIENDLY;
    else if (personalityRoll < 65) traits.type = PersonalityType::NEUTRAL;
    else if (personalityRoll < 75) traits.type = PersonalityType::FEARFUL;
    else if (personalityRoll < 85) traits.type = PersonalityType::CURIOUS;
    else if (personalityRoll < 95) traits.type = PersonalityType::PROTECTIVE;
    else traits.type = PersonalityType::LEADER;

    // Initialisation des traits
    traits.currentEmotion = EmotionalState::CALM;
    traits.bravery = (float)(rand() % 100) / 100.0f;
    traits.sociability = (float)(rand() % 100) / 100.0f;
    traits.aggression = (float)(rand() % 100) / 100.0f;
    traits.intelligence = (float)(rand() % 100) / 100.0f;
    traits.leadership = (float)(rand() % 100) / 100.0f;
    traits.groupInfluence = (int)(traits.leadership * 20.0f); // 0-20 mètres de rayon

    personalities[ped] = traits;

    // Configuration des attributs du PED basés sur la personnalité
    switch (traits.type) {
        case PersonalityType::AGGRESSIVE:
            PED::SET_PED_COMBAT_ABILITY(ped, 100);
            PED::SET_PED_COMBAT_ATTRIBUTES(ped, 46, true);
            break;
        case PersonalityType::CAUTIOUS:
            PED::SET_PED_COMBAT_ABILITY(ped, 50);
            PED::SET_PED_FLEE_ATTRIBUTES(ped, 2, true);
            break;
        case PersonalityType::LEADER:
            PED::SET_PED_COMBAT_ABILITY(ped, 80);
            PED::SET_PED_COMBAT_RANGE(ped, 3);
            break;
    }
}

void PersonalitySystem::updateEmotionalState(Ped ped) {
    auto* traits = getPersonality(ped);
    if (!traits) return;

    Vector3 pedPos = ENTITY::GET_ENTITY_COORDS(ped, true);
    float environmentalStress = calculateEnvironmentalStress(pedPos);

    // Mise à jour de l'état émotionnel basé sur l'environnement
    if (environmentalStress > 0.8f) {
        traits->currentEmotion = EmotionalState::SCARED;
    } else if (environmentalStress > 0.5f) {
        traits->currentEmotion = EmotionalState::NERVOUS;
    } else if (PED::IS_PED_IN_COMBAT(ped, PLAYER::PLAYER_PED_ID())) {
        traits->currentEmotion = EmotionalState::ANGRY;
    } else if (traits->type == PersonalityType::FRIENDLY && environmentalStress < 0.2f) {
        traits->currentEmotion = EmotionalState::HAPPY;
    }

    // Appliquer les effets de l'état émotionnel
    switch (traits->currentEmotion) {
        case EmotionalState::ANGRY:
            traits->aggression = std::min(traits->aggression + 0.1f, 1.0f);
            break;
        case EmotionalState::SCARED:
            traits->bravery = std::max(traits->bravery - 0.1f, 0.0f);
            break;
        case EmotionalState::HAPPY:
            traits->sociability = std::min(traits->sociability + 0.05f, 1.0f);
            break;
    }
}

void PersonalitySystem::influenceNearbyNPCs(Ped ped) {
    auto* traits = getPersonality(ped);
    if (!traits || traits->type != PersonalityType::LEADER) return;

    Vector3 pedPos = ENTITY::GET_ENTITY_COORDS(ped, true);
    const int MAX_NEARBY_PEDS = 10;
    Ped nearbyPeds[MAX_NEARBY_PEDS];
    int count = worldGetAllPeds(nearbyPeds, MAX_NEARBY_PEDS);

    for (int i = 0; i < count; i++) {
        Ped nearbyPed = nearbyPeds[i];
        if (nearbyPed != ped && ENTITY::DOES_ENTITY_EXIST(nearbyPed)) {
            Vector3 nearbyPos = ENTITY::GET_ENTITY_COORDS(nearbyPed, true);
            float distance = SYSTEM::VDIST(pedPos.x, pedPos.y, pedPos.z, nearbyPos.x, nearbyPos.y, nearbyPos.z);

            if (distance < traits->groupInfluence) {
                auto* nearbyTraits = getPersonality(nearbyPed);
                if (nearbyTraits) {
                    // Influence les traits des NPCs proches
                    nearbyTraits->bravery = (nearbyTraits->bravery + traits->bravery) / 2.0f;
                    nearbyTraits->aggression = (nearbyTraits->aggression + traits->aggression) / 2.0f;
                    
                    // Les NPCs suivent l'état émotionnel du leader
                    if (traits->leadership > 0.7f) {
                        nearbyTraits->currentEmotion = traits->currentEmotion;
                    }
                }
            }
        }
    }
}

PersonalitySystem::PersonalityTraits* PersonalitySystem::getPersonality(Ped ped) {
    auto it = personalities.find(ped);
    if (it != personalities.end()) {
        return &it->second;
    }
    return nullptr;
}

float PersonalitySystem::calculateEnvironmentalStress(const Vector3& position) {
    float stress = 0.0f;
    
    // Vérifier les menaces environnementales
    const int MAX_NEARBY_PEDS = 20;
    Ped nearbyPeds[MAX_NEARBY_PEDS];
    int count = worldGetAllPeds(nearbyPeds, MAX_NEARBY_PEDS);
    
    int threateningPeds = 0;
    for (int i = 0; i < count; i++) {
        Ped nearbyPed = nearbyPeds[i];
        if (WEAPON::IS_PED_ARMED(nearbyPed, 7)) {
            threateningPeds++;
        }
    }
    
    stress += (float)threateningPeds / MAX_NEARBY_PEDS;
    
    // Ajouter le stress des explosions ou coups de feu
    if (MISC::GET_NUMBER_OF_FIRES_IN_RANGE(position.x, position.y, position.z, 50.0f) > 0) {
        stress += 0.3f;
    }
    
    return std::min(stress, 1.0f);
}

void PersonalitySystem::handleEnvironmentalInfluence(Ped ped, const Vector3& position) {
    auto* traits = getPersonality(ped);
    if (!traits) return;

    float environmentalStress = calculateEnvironmentalStress(position);
    
    // Réactions basées sur la personnalité et le stress environnemental
    if (environmentalStress > traits->bravery) {
        if (traits->type == PersonalityType::PROTECTIVE) {
            // Protège les NPCs proches
            const int MAX_NEARBY_PEDS = 5;
            Ped nearbyPeds[MAX_NEARBY_PEDS];
            int count = worldGetAllPeds(nearbyPeds, MAX_NEARBY_PEDS);
            
            for (int i = 0; i < count; i++) {
                Ped nearbyPed = nearbyPeds[i];
                if (nearbyPed != ped && !PED::IS_PED_IN_COMBAT(nearbyPed, PLAYER::PLAYER_PED_ID())) {
                    AI::TASK_COMBAT_PED(ped, PLAYER::PLAYER_PED_ID(), 0, 16);
                    break;
                }
            }
        } else if (traits->type == PersonalityType::CURIOUS) {
            // Investigue la source du stress
            AI::TASK_GO_TO_COORD_ANY_MEANS(ped, position.x, position.y, position.z, 2.0f, 0, 0, 786603, 0xbf800000);
        } else if (traits->bravery < 0.3f) {
            // Fuite pour les personnalités peureuses
            AI::TASK_SMART_FLEE_COORD(ped, position.x, position.y, position.z, 100.0f, -1, false, false);
        }
    }
}

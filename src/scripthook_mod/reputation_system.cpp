#include "reputation_system.h"
#include "natives.h"
#include "social_group_system.h"
#include "personality_system.h"

void ReputationSystem::updateReputation(Ped ped, float delta) {
    auto& data = reputations[ped];
    data.reputation = std::clamp(data.reputation + delta, -1.0f, 1.0f);
    
    calculateReputationType(data);
    updateInfluence(ped, data);
    handleReputationEffects(ped, data);
}

void ReputationSystem::recordCrime(Ped ped, float severity) {
    auto& data = reputations[ped];
    data.crimesCommitted++;
    data.notoriety = std::min(data.notoriety + severity, 1.0f);
    updateReputation(ped, -severity * 0.5f);

    // Effet sur les NPCs proches
    const int MAX_WITNESSES = 10;
    Ped witnesses[MAX_WITNESSES];
    int count = worldGetAllPeds(witnesses, MAX_WITNESSES);

    Vector3 crimePos = ENTITY::GET_ENTITY_COORDS(ped, true);
    
    for (int i = 0; i < count; i++) {
        Ped witness = witnesses[i];
        if (witness != ped && ENTITY::DOES_ENTITY_EXIST(witness)) {
            Vector3 witnessPos = ENTITY::GET_ENTITY_COORDS(witness, true);
            float distance = SYSTEM::VDIST(crimePos.x, crimePos.y, crimePos.z, 
                                         witnessPos.x, witnessPos.y, witnessPos.z);
            
            if (distance < 20.0f) {
                // Les témoins réagissent au crime
                auto* personality = PersonalitySystem::getInstance().getPersonality(witness);
                if (personality) {
                    if (personality->type == PersonalityType::CAUTIOUS) {
                        AI::TASK_SMART_FLEE_PED(witness, ped, 100.0f, -1, false, false);
                    } else if (personality->bravery > 0.7f) {
                        AI::TASK_COMBAT_PED(witness, ped, 0, 16);
                    }
                }
            }
        }
    }
}

void ReputationSystem::recordGoodDeed(Ped ped, float value) {
    auto& data = reputations[ped];
    data.goodDeeds++;
    updateReputation(ped, value);

    // Propager la bonne réputation
    propagateReputation(ped, 30.0f);
}

void ReputationSystem::updateSocialStatus(Ped ped) {
    auto& data = reputations[ped];
    
    // Calculer le statut social basé sur la réputation et l'influence
    float score = (data.reputation + 1.0f) * 0.5f + data.influence;
    
    if (score > 1.8f) data.status = SocialStatus::LEGENDARY;
    else if (score > 1.5f) data.status = SocialStatus::LEADER;
    else if (score > 1.2f) data.status = SocialStatus::INFLUENTIAL;
    else if (score > 0.8f) data.status = SocialStatus::RESPECTED;
    else if (score > 0.4f) data.status = SocialStatus::MEMBER;
    else data.status = SocialStatus::OUTSIDER;

    // Appliquer les effets du statut social
    switch (data.status) {
        case SocialStatus::LEGENDARY:
            // Les NPCs s'inclinent ou saluent
            PED::SET_PED_CAN_BE_TARGETTED_BY_PLAYER(ped, false);
            break;
        case SocialStatus::LEADER:
            // Augmenter le charisme et l'influence
            data.influence = std::min(data.influence + 0.1f, 1.0f);
            break;
        case SocialStatus::OUTSIDER:
            // Les NPCs évitent ou ignorent
            data.influence = std::max(data.influence - 0.1f, 0.0f);
            break;
    }
}

void ReputationSystem::propagateReputation(Ped ped, float radius) {
    auto* sourceData = getReputation(ped);
    if (!sourceData) return;

    Vector3 sourcePos = ENTITY::GET_ENTITY_COORDS(ped, true);
    const int MAX_NEARBY = 20;
    Ped nearbyPeds[MAX_NEARBY];
    int count = worldGetAllPeds(nearbyPeds, MAX_NEARBY);

    for (int i = 0; i < count; i++) {
        Ped nearbyPed = nearbyPeds[i];
        if (nearbyPed != ped && ENTITY::DOES_ENTITY_EXIST(nearbyPed)) {
            Vector3 nearbyPos = ENTITY::GET_ENTITY_COORDS(nearbyPed, true);
            float distance = SYSTEM::VDIST(sourcePos.x, sourcePos.y, sourcePos.z,
                                         nearbyPos.x, nearbyPos.y, nearbyPos.z);

            if (distance < radius) {
                float influence = (1.0f - (distance / radius)) * sourceData->influence;
                updateReputation(nearbyPed, influence * 0.1f);
            }
        }
    }
}

void ReputationSystem::calculateReputationType(ReputationData& data) {
    if (data.notoriety > 0.8f) {
        data.type = ReputationType::FEARED;
    } else if (data.reputation > 0.7f) {
        data.type = ReputationType::HERO;
    } else if (data.reputation < -0.7f) {
        data.type = ReputationType::CRIMINAL;
    } else if (data.reputation > 0.3f) {
        data.type = ReputationType::FRIENDLY;
    } else if (data.reputation < -0.3f) {
        data.type = ReputationType::HOSTILE;
    } else {
        data.type = ReputationType::NEUTRAL;
    }
}

void ReputationSystem::updateInfluence(Ped ped, ReputationData& data) {
    // L'influence augmente avec les bonnes actions et le statut social
    float goodDeedInfluence = std::min((float)data.goodDeeds / 100.0f, 0.5f);
    float reputationInfluence = std::max(data.reputation, 0.0f);
    
    data.influence = std::clamp(goodDeedInfluence + reputationInfluence, 0.0f, 1.0f);
}

void ReputationSystem::handleReputationEffects(Ped ped, ReputationData& data) {
    // Appliquer des effets basés sur la réputation
    switch (data.type) {
        case ReputationType::FEARED:
            // Les NPCs fuient
            PED::SET_PED_COMBAT_ABILITY(ped, 100);
            break;
        case ReputationType::HERO:
            // Les NPCs aident et suivent
            PED::SET_PED_AS_GROUP_LEADER(ped, true);
            break;
        case ReputationType::CRIMINAL:
            // Les NPCs appellent la police
            PED::SET_PED_COMBAT_ATTRIBUTES(ped, 46, true);
            break;
    }
}

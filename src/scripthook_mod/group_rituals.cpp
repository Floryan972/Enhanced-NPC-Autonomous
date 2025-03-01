#include "group_rituals.h"
#include "natives.h"
#include "social_hierarchy.h"
#include "collective_memory.h"
#include "personality_system.h"

void GroupRituals::initializeRituals(const std::string& groupId) {
    std::vector<Ritual> rituals;

    // Rituel d'initiation
    {
        Ritual initiation;
        initiation.type = RitualType::INITIATION;
        initiation.importance = 0.9f;
        
        RitualPhase preparation;
        preparation.name = "preparation";
        preparation.duration = 60.0f;
        preparation.animations = {"WORLD_HUMAN_GUARD_STAND"};
        preparation.requiresLeader = true;
        
        RitualPhase ceremony;
        ceremony.name = "ceremony";
        ceremony.duration = 120.0f;
        ceremony.animations = {"WORLD_HUMAN_GUARD_PATROL"};
        ceremony.requiresLeader = true;
        
        initiation.phases = {preparation, ceremony};
        rituals.push_back(initiation);
    }

    // Rituel de célébration
    {
        Ritual celebration;
        celebration.type = RitualType::CELEBRATION;
        celebration.importance = 0.7f;
        
        RitualPhase gathering;
        gathering.name = "gathering";
        gathering.duration = 30.0f;
        gathering.animations = {"WORLD_HUMAN_PARTYING"};
        
        RitualPhase feast;
        feast.name = "feast";
        feast.duration = 180.0f;
        feast.animations = {"WORLD_HUMAN_DRINKING"};
        
        celebration.phases = {gathering, feast};
        rituals.push_back(celebration);
    }

    groupRituals[groupId] = rituals;
}

void GroupRituals::updateRituals() {
    float deltaTime = MISC::GET_FRAME_TIME();
    
    for (auto it = activeRituals.begin(); it != activeRituals.end();) {
        auto& ritual = it->second;
        
        if (ritual.isActive) {
            ritual.timeRemaining -= deltaTime;
            
            if (ritual.timeRemaining <= 0.0f) {
                // Passer à la phase suivante
                ritual.currentPhase++;
                
                if (ritual.currentPhase >= ritual.phases.size()) {
                    // Rituel terminé
                    handleRitualOutcome(it->first, true);
                    it = activeRituals.erase(it);
                    continue;
                } else {
                    // Initialiser la nouvelle phase
                    ritual.timeRemaining = ritual.phases[ritual.currentPhase].duration;
                    updateRitualPhase(ritual);
                }
            } else {
                // Mettre à jour les participants
                positionParticipants(ritual);
                createRitualEffects(ritual);
            }
        }
        
        ++it;
    }
}

void GroupRituals::startRitual(const std::string& groupId, RitualType type) {
    // Trouver le rituel approprié
    for (const auto& ritual : groupRituals[groupId]) {
        if (ritual.type == type) {
            // Créer une nouvelle instance active
            std::string ritualId = groupId + "_" + std::to_string(MISC::GET_GAME_TIMER());
            Ritual activeRitual = ritual;
            activeRitual.isActive = true;
            activeRitual.currentPhase = 0;
            activeRitual.timeRemaining = ritual.phases[0].duration;
            
            // Trouver une location appropriée
            Vector3 groupCenter = ENTITY::GET_ENTITY_COORDS(
                SocialHierarchy::getInstance().getGroupLeader(groupId),
                true
            );
            activeRitual.location = groupCenter;
            
            // Ajouter les participants initiaux
            const auto& group = SocialGroupSystem::getInstance().getGroup(groupId);
            for (const auto& member : group.members) {
                if (ENTITY::DOES_ENTITY_EXIST(member.pedHandle)) {
                    activeRitual.participants.push_back(member.pedHandle);
                }
            }
            
            activeRituals[ritualId] = activeRitual;
            
            // Enregistrer le début du rituel dans la mémoire collective
            recordRitualMemory(groupId, activeRitual);
            break;
        }
    }
}

void GroupRituals::updateRitualPhase(Ritual& ritual) {
    const auto& phase = ritual.phases[ritual.currentPhase];
    
    // Vérifier si le leader est nécessaire
    if (phase.requiresLeader) {
        bool leaderPresent = false;
        for (Ped participant : ritual.participants) {
            if (SocialHierarchy::getInstance().getRank(participant) == HierarchyRank::LEADER) {
                leaderPresent = true;
                break;
            }
        }
        
        if (!leaderPresent) {
            ritual.isActive = false;
            return;
        }
    }

    // Mettre à jour les positions des participants
    positionParticipants(ritual);
    
    // Appliquer les animations de la phase
    for (size_t i = 0; i < ritual.participants.size(); i++) {
        Ped participant = ritual.participants[i];
        if (!ENTITY::DOES_ENTITY_EXIST(participant)) continue;

        const std::string& animation = phase.animations[i % phase.animations.size()];
        AI::TASK_START_SCENARIO_IN_PLACE(participant, animation.c_str(), 0, true);
    }
}

void GroupRituals::positionParticipants(Ritual& ritual) {
    const auto& phase = ritual.phases[ritual.currentPhase];
    float radius = 5.0f;
    
    for (size_t i = 0; i < ritual.participants.size(); i++) {
        Ped participant = ritual.participants[i];
        if (!ENTITY::DOES_ENTITY_EXIST(participant)) continue;

        // Calculer la position en cercle
        float angle = (2.0f * 3.14159f * i) / ritual.participants.size();
        Vector3 targetPos = {
            ritual.location.x + radius * cos(angle),
            ritual.location.y + radius * sin(angle),
            ritual.location.z
        };

        // Déplacer le participant
        AI::TASK_GO_TO_COORD_ANY_MEANS(
            participant,
            targetPos.x, targetPos.y, targetPos.z,
            2.0f, 0, 0, 786603, 0xbf800000
        );
    }
}

void GroupRituals::createRitualEffects(const Ritual& ritual) {
    // Créer des effets visuels selon le type de rituel
    switch (ritual.type) {
        case RitualType::CELEBRATION:
            GRAPHICS::USE_PARTICLE_FX_ASSET("scr_rcpaparazzo1");
            GRAPHICS::START_PARTICLE_FX_NON_LOOPED_AT_COORD(
                "scr_mich4_firework_sparkle_spawn",
                ritual.location.x, ritual.location.y, ritual.location.z + 10.0f,
                0.0f, 0.0f, 0.0f, 1.0f, false, false, false
            );
            break;

        case RitualType::MOURNING:
            GRAPHICS::USE_PARTICLE_FX_ASSET("scr_solomon3");
            GRAPHICS::START_PARTICLE_FX_NON_LOOPED_AT_COORD(
                "scr_trev4_747_blood_impact",
                ritual.location.x, ritual.location.y, ritual.location.z,
                0.0f, 0.0f, 0.0f, 1.0f, false, false, false
            );
            break;
    }
}

void GroupRituals::recordRitualMemory(const std::string& groupId, const Ritual& ritual) {
    CollectiveMemoryEvent ritualEvent;
    ritualEvent.type = MemoryType::POSITIVE;
    ritualEvent.importance = ritual.importance;
    ritualEvent.location = ritual.location;
    ritualEvent.timeStamp = MISC::GET_GAME_TIMER() / 1000.0f;
    ritualEvent.description = "group_ritual_" + std::to_string(static_cast<int>(ritual.type));
    ritualEvent.involvedPeds = ritual.participants;

    CollectiveMemory::getInstance().recordEvent(groupId, ritualEvent);
}

void GroupRituals::handleRitualOutcome(const std::string& ritualId, bool success) {
    auto it = activeRituals.find(ritualId);
    if (it == activeRituals.end()) return;

    const auto& ritual = it->second;
    
    // Effets sur les participants
    for (Ped participant : ritual.participants) {
        if (!ENTITY::DOES_ENTITY_EXIST(participant)) continue;

        auto* personality = PersonalitySystem::getInstance().getPersonality(participant);
        if (personality) {
            if (success) {
                // Renforcer les liens sociaux
                personality->happiness += 0.2f;
                personality->stress -= 0.1f;
            } else {
                // Effets négatifs
                personality->stress += 0.2f;
            }
        }
    }

    // Mettre à jour la mémoire collective
    std::string groupId = ritualId.substr(0, ritualId.find('_'));
    CollectiveMemoryEvent outcomeEvent;
    outcomeEvent.type = success ? MemoryType::POSITIVE : MemoryType::NEGATIVE;
    outcomeEvent.importance = ritual.importance;
    outcomeEvent.location = ritual.location;
    outcomeEvent.timeStamp = MISC::GET_GAME_TIMER() / 1000.0f;
    outcomeEvent.description = "ritual_outcome_" + std::to_string(success);
    outcomeEvent.involvedPeds = ritual.participants;

    CollectiveMemory::getInstance().recordEvent(groupId, outcomeEvent);
}

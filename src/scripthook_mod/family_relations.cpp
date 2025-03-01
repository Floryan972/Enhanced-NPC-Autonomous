#include "family_relations.h"
#include "natives.h"
#include "personality_system.h"
#include "collective_memory.h"
#include "group_rituals.h"

void FamilyRelations::initializeFamily(const std::string& familyId) {
    Family family;
    family.familyId = familyId;
    family.familyHonor = 1.0f;
    family.stability = 1.0f;
    
    // Traditions de base
    family.traditions = {
        "family_dinner",
        "respect_elders",
        "protect_members"
    };
    
    families[familyId] = family;
}

void FamilyRelations::updateFamilies() {
    for (auto& [familyId, family] : families) {
        // Mettre à jour les liens familiaux
        updateFamilyBonds(family);
        
        // Gérer les changements générationnels
        handleGenerationalChange(family);
        
        // Maintenir les traditions
        maintainTraditions(family);
        
        // Résoudre les conflits internes
        resolveInternalConflicts(family);
        
        // Mettre à jour les comportements familiaux
        for (auto& member : family.members) {
            if (!ENTITY::DOES_ENTITY_EXIST(member.ped)) continue;

            // Comportements basés sur la relation
            switch (member.relation) {
                case RelationType::PARENT:
                    // Les parents protègent leurs enfants
                    for (const auto& otherMember : family.members) {
                        if (otherMember.relation == RelationType::CHILD) {
                            if (ENTITY::DOES_ENTITY_EXIST(otherMember.ped)) {
                                Vector3 childPos = ENTITY::GET_ENTITY_COORDS(otherMember.ped, true);
                                float distance = SYSTEM::VDIST(
                                    ENTITY::GET_ENTITY_COORDS(member.ped, true).x,
                                    ENTITY::GET_ENTITY_COORDS(member.ped, true).y,
                                    ENTITY::GET_ENTITY_COORDS(member.ped, true).z,
                                    childPos.x, childPos.y, childPos.z
                                );

                                if (distance > 20.0f) {
                                    AI::TASK_GO_TO_ENTITY(member.ped, otherMember.ped, -1, 5.0f, 2.0f, 0);
                                }
                            }
                        }
                    }
                    break;

                case RelationType::CHILD:
                    // Les enfants suivent leurs parents
                    for (const auto& otherMember : family.members) {
                        if (otherMember.relation == RelationType::PARENT) {
                            if (ENTITY::DOES_ENTITY_EXIST(otherMember.ped)) {
                                AI::TASK_FOLLOW_TO_OFFSET_OF_ENTITY(
                                    member.ped,
                                    otherMember.ped,
                                    0.0f, -3.0f, 0.0f,
                                    1.0f, -1, 2.0f, true
                                );
                            }
                        }
                    }
                    break;
            }
        }
    }
}

void FamilyRelations::updateFamilyBonds(Family& family) {
    for (auto& member : family.members) {
        if (!ENTITY::DOES_ENTITY_EXIST(member.ped)) continue;

        // Mettre à jour la proximité avec les autres membres
        for (auto& otherMember : family.members) {
            if (member.ped == otherMember.ped) continue;
            if (!ENTITY::DOES_ENTITY_EXIST(otherMember.ped)) continue;

            Vector3 pos1 = ENTITY::GET_ENTITY_COORDS(member.ped, true);
            Vector3 pos2 = ENTITY::GET_ENTITY_COORDS(otherMember.ped, true);
            
            float distance = SYSTEM::VDIST(
                pos1.x, pos1.y, pos1.z,
                pos2.x, pos2.y, pos2.z
            );

            // La proximité augmente quand les membres sont proches
            if (distance < 10.0f) {
                member.closeness = std::min(member.closeness + 0.01f, 1.0f);
            } else {
                member.closeness = std::max(member.closeness - 0.001f, 0.0f);
            }
        }

        // Mettre à jour la loyauté basée sur les interactions
        auto* personality = PersonalitySystem::getInstance().getPersonality(member.ped);
        if (personality) {
            member.loyalty = std::clamp(
                member.loyalty + 
                (personality->happiness - personality->stress) * 0.01f,
                0.0f, 1.0f
            );
        }
    }
}

void FamilyRelations::organizeFamilyGathering(const std::string& familyId) {
    auto& family = families[familyId];
    
    // Trouver un lieu de rassemblement
    Vector3 gatheringSpot = family.homeLocation;
    
    // Créer un rituel familial
    Ritual familyRitual;
    familyRitual.type = RitualType::GATHERING;
    familyRitual.importance = 0.8f;
    familyRitual.location = gatheringSpot;
    
    // Ajouter les phases du rituel
    RitualPhase greeting;
    greeting.name = "family_greeting";
    greeting.duration = 30.0f;
    greeting.animations = {"WORLD_HUMAN_CHEERING"};
    
    RitualPhase meal;
    meal.name = "family_meal";
    meal.duration = 300.0f;
    meal.animations = {"WORLD_HUMAN_SEAT_WALL_EATING"};
    
    familyRitual.phases = {greeting, meal};
    
    // Ajouter tous les membres de la famille comme participants
    for (const auto& member : family.members) {
        if (ENTITY::DOES_ENTITY_EXIST(member.ped)) {
            familyRitual.participants.push_back(member.ped);
        }
    }
    
    // Démarrer le rituel
    GroupRituals::getInstance().startRitual(familyId, RitualType::GATHERING);
    
    // Créer un souvenir familial
    CollectiveMemoryEvent gatheringMemory;
    gatheringMemory.type = MemoryType::POSITIVE;
    gatheringMemory.importance = 0.8f;
    gatheringMemory.location = gatheringSpot;
    gatheringMemory.description = "family_gathering";
    gatheringMemory.involvedPeds = familyRitual.participants;
    
    CollectiveMemory::getInstance().recordEvent(familyId, gatheringMemory);
}

void FamilyRelations::handleFamilyConflict(Ped ped1, Ped ped2) {
    std::string familyId1 = pedToFamily[ped1];
    std::string familyId2 = pedToFamily[ped2];
    
    if (familyId1 == familyId2) {
        // Conflit interne à la famille
        auto& family = families[familyId1];
        
        // Trouver le membre le plus respecté pour médier
        FamilyMember* mediator = nullptr;
        float highestLoyalty = -1.0f;
        
        for (auto& member : family.members) {
            if (member.ped != ped1 && member.ped != ped2 && 
                member.loyalty > highestLoyalty) {
                mediator = &member;
                highestLoyalty = member.loyalty;
            }
        }

        if (mediator) {
            // Organiser une médiation
            Vector3 mediatorPos = ENTITY::GET_ENTITY_COORDS(mediator->ped, true);
            
            AI::TASK_GO_TO_COORD_ANY_MEANS(ped1,
                mediatorPos.x - 1.0f, mediatorPos.y, mediatorPos.z,
                2.0f, 0, 0, 786603, 0xbf800000
            );
            
            AI::TASK_GO_TO_COORD_ANY_MEANS(ped2,
                mediatorPos.x + 1.0f, mediatorPos.y, mediatorPos.z,
                2.0f, 0, 0, 786603, 0xbf800000
            );

            // Impact sur l'honneur familial
            family.familyHonor *= 0.9f;
            family.stability *= 0.9f;
        }
    } else {
        // Conflit entre familles
        auto& family1 = families[familyId1];
        auto& family2 = families[familyId2];
        
        // Impact sur les relations entre familles
        family1.familyHonor *= 0.95f;
        family2.familyHonor *= 0.95f;
        
        // Créer un souvenir du conflit
        CollectiveMemoryEvent conflictMemory;
        conflictMemory.type = MemoryType::NEGATIVE;
        conflictMemory.importance = 0.7f;
        conflictMemory.mainActor = ped1;
        conflictMemory.involvedPeds = {ped1, ped2};
        conflictMemory.description = "family_conflict";
        
        CollectiveMemory::getInstance().recordEvent(familyId1, conflictMemory);
        CollectiveMemory::getInstance().recordEvent(familyId2, conflictMemory);
    }
}

void FamilyRelations::passFamilyTradition(const std::string& familyId, const std::string& tradition) {
    auto& family = families[familyId];
    
    // Trouver un ancien pour enseigner
    FamilyMember* elder = nullptr;
    for (auto& member : family.members) {
        if (member.relation == RelationType::PARENT && member.loyalty > 0.7f) {
            elder = &member;
            break;
        }
    }

    if (elder) {
        // Rassembler les jeunes membres
        std::vector<Ped> youngMembers;
        for (const auto& member : family.members) {
            if (member.relation == RelationType::CHILD) {
                youngMembers.push_back(member.ped);
            }
        }

        if (!youngMembers.empty()) {
            // Créer un rituel d'enseignement
            Ritual teachingRitual;
            teachingRitual.type = RitualType::CEREMONY;
            teachingRitual.importance = 0.9f;
            teachingRitual.location = family.homeLocation;
            teachingRitual.participants = youngMembers;
            
            // Ajouter l'ancien comme participant principal
            teachingRitual.participants.insert(teachingRitual.participants.begin(), elder->ped);
            
            // Démarrer le rituel
            GroupRituals::getInstance().startRitual(familyId, RitualType::CEREMONY);
            
            // Renforcer les liens familiaux
            for (auto& member : family.members) {
                member.loyalty = std::min(member.loyalty + 0.1f, 1.0f);
            }
            
            // Augmenter l'honneur familial
            family.familyHonor = std::min(family.familyHonor + 0.1f, 1.0f);
        }
    }
}

#include "social_hierarchy.h"
#include "natives.h"
#include "personality_system.h"
#include "group_learning.h"
#include "collective_memory.h"

void SocialHierarchy::initializeHierarchy(const std::string& groupId) {
    auto& hierarchy = groupHierarchies[groupId];
    
    // Trouver le meilleur candidat pour leader
    const auto& group = SocialGroupSystem::getInstance().getGroup(groupId);
    Ped bestLeader = 0;
    float bestScore = -1.0f;
    
    for (const auto& member : group.members) {
        auto* personality = PersonalitySystem::getInstance().getPersonality(member.pedHandle);
        if (!personality) continue;

        float leadershipScore = personality->charisma * 0.4f + 
                              personality->intelligence * 0.3f +
                              personality->bravery * 0.3f;
        
        if (leadershipScore > bestScore) {
            bestScore = leadershipScore;
            bestLeader = member.pedHandle;
        }
    }

    // Créer la hiérarchie initiale
    if (bestLeader != 0) {
        HierarchyNode leaderNode;
        leaderNode.ped = bestLeader;
        leaderNode.rank = HierarchyRank::LEADER;
        leaderNode.authority = 1.0f;
        leaderNode.superior = nullptr;
        
        hierarchy.push_back(leaderNode);
        
        // Initialiser la position sociale du leader
        SocialPosition leaderPos;
        leaderPos.rank = HierarchyRank::LEADER;
        leaderPos.influence = 1.0f;
        leaderPos.respect = 1.0f;
        socialPositions[bestLeader] = leaderPos;
    }
}

void SocialHierarchy::updateHierarchy() {
    for (auto& [groupId, hierarchy] : groupHierarchies) {
        // Mettre à jour l'autorité de chaque membre
        for (auto& node : hierarchy) {
            updateAuthority(&node);
        }

        // Résoudre les conflits potentiels
        resolveConflicts(groupId);
        
        // Équilibrer le pouvoir
        balancePower(groupId);
        
        // Mettre à jour les comportements basés sur la hiérarchie
        for (auto& node : hierarchy) {
            auto& position = socialPositions[node.ped];
            
            // Appliquer les effets de rang
            switch (node.rank) {
                case HierarchyRank::LEADER:
                    // Le leader donne des ordres
                    for (auto* subordinate : node.subordinates) {
                        if (ENTITY::DOES_ENTITY_EXIST(subordinate->ped)) {
                            AI::TASK_FOLLOW_TO_OFFSET_OF_ENTITY(
                                subordinate->ped,
                                node.ped,
                                0.0f, -3.0f, 0.0f,
                                1.0f, -1, 2.0f, true
                            );
                        }
                    }
                    break;

                case HierarchyRank::ELDER:
                    // Les anciens enseignent
                    for (Ped mentee : position.mentees) {
                        if (ENTITY::DOES_ENTITY_EXIST(mentee)) {
                            GroupLearning::getInstance().teachBehavior(
                                node.ped,
                                mentee,
                                "elder_wisdom"
                            );
                        }
                    }
                    break;

                case HierarchyRank::ENFORCER:
                    // Les exécuteurs patrouillent
                    if (ENTITY::DOES_ENTITY_EXIST(node.ped)) {
                        AI::TASK_PATROL(
                            node.ped,
                            "GROUP_PATROL",
                            0, true,
                            true
                        );
                    }
                    break;
            }
        }
    }
}

void SocialHierarchy::handleSuccession(const std::string& groupId, Ped oldLeader) {
    auto& hierarchy = groupHierarchies[groupId];
    
    // Trouver les candidats potentiels
    std::vector<HierarchyNode*> candidates;
    for (auto& node : hierarchy) {
        if (node.rank == HierarchyRank::ELDER || node.rank == HierarchyRank::VETERAN) {
            candidates.push_back(&node);
        }
    }

    // Évaluer chaque candidat
    HierarchyNode* bestCandidate = nullptr;
    float bestScore = -1.0f;

    for (auto* candidate : candidates) {
        auto* personality = PersonalitySystem::getInstance().getPersonality(candidate->ped);
        if (!personality) continue;

        float successionScore = candidate->authority * 0.4f +
                              personality->charisma * 0.3f +
                              socialPositions[candidate->ped].respect * 0.3f;

        if (successionScore > bestScore) {
            bestScore = successionScore;
            bestCandidate = candidate;
        }
    }

    // Installer le nouveau leader
    if (bestCandidate) {
        bestCandidate->rank = HierarchyRank::LEADER;
        bestCandidate->authority = 1.0f;
        bestCandidate->superior = nullptr;

        // Mettre à jour la position sociale
        auto& position = socialPositions[bestCandidate->ped];
        position.rank = HierarchyRank::LEADER;
        position.influence = 1.0f;

        // Créer un événement mémorable
        CollectiveMemoryEvent successionEvent;
        successionEvent.type = MemoryType::POSITIVE;
        successionEvent.importance = 1.0f;
        successionEvent.mainActor = bestCandidate->ped;
        successionEvent.description = "leadership_succession";
        
        CollectiveMemory::getInstance().recordEvent(groupId, successionEvent);
    }
}

void SocialHierarchy::mediateConflict(Ped ped1, Ped ped2) {
    auto* pos1 = &socialPositions[ped1];
    auto* pos2 = &socialPositions[ped2];
    
    // Trouver un médiateur
    Ped mediator = 0;
    float bestMediatorScore = -1.0f;
    
    for (const auto& [ped, position] : socialPositions) {
        if (ped == ped1 || ped == ped2) continue;
        
        if (position.rank == HierarchyRank::ELDER || 
            std::find(position.roles.begin(), position.roles.end(), SocialRole::MEDIATOR) != position.roles.end()) {
            float mediatorScore = position.respect * 0.6f + position.influence * 0.4f;
            
            if (mediatorScore > bestMediatorScore) {
                bestMediatorScore = mediatorScore;
                mediator = ped;
            }
        }
    }

    if (mediator != 0) {
        // Organiser la médiation
        Vector3 mediatorPos = ENTITY::GET_ENTITY_COORDS(mediator, true);
        
        AI::TASK_GO_TO_COORD_ANY_MEANS(ped1, 
            mediatorPos.x - 1.0f, mediatorPos.y, mediatorPos.z,
            2.0f, 0, 0, 786603, 0xbf800000
        );
        
        AI::TASK_GO_TO_COORD_ANY_MEANS(ped2,
            mediatorPos.x + 1.0f, mediatorPos.y, mediatorPos.z,
            2.0f, 0, 0, 786603, 0xbf800000
        );

        // Ajuster les relations
        pos1->respect *= 0.9f;
        pos2->respect *= 0.9f;
        socialPositions[mediator].respect *= 1.1f;
    }
}

void SocialHierarchy::updateAuthority(HierarchyNode* node) {
    if (!node) return;

    // Facteurs influençant l'autorité
    float subordinateInfluence = 0.0f;
    for (auto* sub : node->subordinates) {
        subordinateInfluence += sub->authority * 0.1f;
    }

    auto* personality = PersonalitySystem::getInstance().getPersonality(node->ped);
    if (personality) {
        node->authority = std::clamp(
            node->authority * 0.8f +                    // Inertie
            subordinateInfluence +                      // Influence des subordonnés
            personality->charisma * 0.1f +             // Charisme
            socialPositions[node->ped].respect * 0.1f,  // Respect
            0.0f, 1.0f
        );
    }

    // Propager l'autorité aux subordonnés
    for (auto* sub : node->subordinates) {
        sub->authority = std::min(sub->authority, node->authority * 0.8f);
    }
}

void SocialHierarchy::balancePower(const std::string& groupId) {
    auto& hierarchy = groupHierarchies[groupId];
    
    // Calculer le pouvoir total
    float totalPower = 0.0f;
    for (const auto& node : hierarchy) {
        totalPower += node.authority;
    }

    // Ajuster si le pouvoir est trop concentré
    if (totalPower > 0.0f) {
        float averagePower = totalPower / hierarchy.size();
        
        for (auto& node : hierarchy) {
            if (node.authority > averagePower * 2.0f) {
                // Redistribuer l'excès de pouvoir
                float excess = node.authority - (averagePower * 1.5f);
                node.authority -= excess;
                
                // Distribuer aux subordonnés
                if (!node.subordinates.empty()) {
                    float sharePerSubordinate = excess / node.subordinates.size();
                    for (auto* sub : node.subordinates) {
                        sub->authority += sharePerSubordinate;
                    }
                }
            }
        }
    }
}

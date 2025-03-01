#include "social_group_system.h"
#include "natives.h"
#include "personality_system.h"
#include <algorithm>
#include <random>

std::string SocialGroupSystem::createGroup(GroupType type, const Vector3& baseLocation) {
    static int groupCounter = 0;
    std::string groupId = "group_" + std::to_string(groupCounter++);
    
    Group newGroup;
    newGroup.groupId = groupId;
    newGroup.type = type;
    newGroup.baseLocation = baseLocation;
    newGroup.groupCohesion = 1.0f;
    newGroup.territorialRadius = 100.0f;
    newGroup.currentActivity = GroupActivity::IDLE;
    
    groups[groupId] = newGroup;
    return groupId;
}

void SocialGroupSystem::addMemberToGroup(const std::string& groupId, Ped ped, bool isLeader) {
    auto it = groups.find(groupId);
    if (it == groups.end()) return;

    GroupMember member;
    member.pedHandle = ped;
    member.isLeader = isLeader;
    member.influence = isLeader ? 1.0f : 0.5f;
    member.lastKnownPos = ENTITY::GET_ENTITY_COORDS(ped, true);
    member.currentActivity = it->second.currentActivity;

    it->second.members.push_back(member);

    // Configurer les relations avec les autres membres
    PED::SET_PED_RELATIONSHIP_GROUP_HASH(ped, MISC::GET_HASH_KEY(groupId.c_str()));
}

void SocialGroupSystem::updateGroups() {
    for (auto& [groupId, group] : groups) {
        updateGroupCohesion(group);
        handleGroupFormation(group);
        updateGroupBehavior(group);
        
        // Nettoyer les membres invalides
        group.members.erase(
            std::remove_if(
                group.members.begin(),
                group.members.end(),
                [](const GroupMember& member) {
                    return !ENTITY::DOES_ENTITY_EXIST(member.pedHandle);
                }
            ),
            group.members.end()
        );
    }
}

void SocialGroupSystem::updateGroupCohesion(Group& group) {
    if (group.members.empty()) return;

    Vector3 center = calculateGroupCenter(group);
    float maxDistance = 0.0f;

    // Calculer la cohésion basée sur la distance entre les membres
    for (auto& member : group.members) {
        Vector3 memberPos = ENTITY::GET_ENTITY_COORDS(member.pedHandle, true);
        float distance = SYSTEM::VDIST(
            memberPos.x, memberPos.y, memberPos.z,
            center.x, center.y, center.z
        );
        maxDistance = std::max(maxDistance, distance);
    }

    // Mettre à jour la cohésion
    group.groupCohesion = 1.0f - std::min(maxDistance / group.territorialRadius, 1.0f);
}

void SocialGroupSystem::handleGroupFormation(Group& group) {
    if (group.members.size() < 2) return;

    Vector3 center = calculateGroupCenter(group);
    
    // Trouver le leader
    GroupMember* leader = nullptr;
    for (auto& member : group.members) {
        if (member.isLeader) {
            leader = &member;
            break;
        }
    }

    // Formation en fonction du type de groupe
    switch (group.type) {
        case GroupType::GANG:
            // Formation agressive en V
            if (leader) {
                float spacing = 2.0f;
                int position = 0;
                
                for (auto& member : group.members) {
                    if (!member.isLeader) {
                        Vector3 leaderPos = ENTITY::GET_ENTITY_COORDS(leader->pedHandle, true);
                        float offset = (position % 2 == 0) ? spacing : -spacing;
                        
                        AI::TASK_GO_TO_COORD_ANY_MEANS(
                            member.pedHandle,
                            leaderPos.x - spacing,
                            leaderPos.y + offset,
                            leaderPos.z,
                            2.0f, 0, 0, 786603, 0xbf800000
                        );
                        position++;
                    }
                }
            }
            break;

        case GroupType::POLICE:
            // Formation tactique
            if (leader) {
                int position = 0;
                for (auto& member : group.members) {
                    if (!member.isLeader) {
                        Vector3 leaderPos = ENTITY::GET_ENTITY_COORDS(leader->pedHandle, true);
                        float angle = (position * 90.0f) * 3.14159f / 180.0f;
                        float radius = 3.0f;
                        
                        AI::TASK_GO_TO_COORD_ANY_MEANS(
                            member.pedHandle,
                            leaderPos.x + cos(angle) * radius,
                            leaderPos.y + sin(angle) * radius,
                            leaderPos.z,
                            2.0f, 0, 0, 786603, 0xbf800000
                        );
                        position++;
                    }
                }
            }
            break;

        default:
            // Formation sociale détendue
            for (auto& member : group.members) {
                if (!member.isLeader) {
                    AI::TASK_GO_TO_COORD_ANY_MEANS(
                        member.pedHandle,
                        center.x + (rand() % 5 - 2),
                        center.y + (rand() % 5 - 2),
                        center.z,
                        2.0f, 0, 0, 786603, 0xbf800000
                    );
                }
            }
            break;
    }
}

void SocialGroupSystem::updateGroupBehavior(Group& group) {
    switch (group.currentActivity) {
        case GroupActivity::PATROLLING:
            if (!group.territoryPoints.empty()) {
                static size_t currentPoint = 0;
                Vector3 target = group.territoryPoints[currentPoint];
                
                for (auto& member : group.members) {
                    AI::TASK_GO_TO_COORD_ANY_MEANS(
                        member.pedHandle,
                        target.x, target.y, target.z,
                        2.0f, 0, 0, 786603, 0xbf800000
                    );
                }
                
                // Passer au point suivant si le groupe est proche
                Vector3 groupPos = calculateGroupCenter(group);
                if (SYSTEM::VDIST(groupPos.x, groupPos.y, groupPos.z, target.x, target.y, target.z) < 5.0f) {
                    currentPoint = (currentPoint + 1) % group.territoryPoints.size();
                }
            }
            break;

        case GroupActivity::SOCIALIZING:
            for (auto& member : group.members) {
                // Animations sociales aléatoires
                switch (rand() % 3) {
                    case 0:
                        AI::TASK_START_SCENARIO_IN_PLACE(member.pedHandle, "WORLD_HUMAN_STAND_IMPATIENT", 0, true);
                        break;
                    case 1:
                        AI::TASK_START_SCENARIO_IN_PLACE(member.pedHandle, "WORLD_HUMAN_HANG_OUT_STREET", 0, true);
                        break;
                    case 2:
                        AI::TASK_START_SCENARIO_IN_PLACE(member.pedHandle, "WORLD_HUMAN_SMOKING", 0, true);
                        break;
                }
            }
            break;

        case GroupActivity::PROTECTING:
            {
                Vector3 center = calculateGroupCenter(group);
                float radius = group.territorialRadius;
                
                // Vérifier les menaces
                const int MAX_THREATS = 10;
                Ped threats[MAX_THREATS];
                int count = worldGetAllPeds(threats, MAX_THREATS);
                
                for (int i = 0; i < count; i++) {
                    Ped threat = threats[i];
                    if (ENTITY::DOES_ENTITY_EXIST(threat)) {
                        Vector3 threatPos = ENTITY::GET_ENTITY_COORDS(threat, true);
                        float distance = SYSTEM::VDIST(center.x, center.y, center.z, threatPos.x, threatPos.y, threatPos.z);
                        
                        if (distance < radius && WEAPON::IS_PED_ARMED(threat, 7)) {
                            // Réagir à la menace
                            for (auto& member : group.members) {
                                AI::TASK_COMBAT_PED(member.pedHandle, threat, 0, 16);
                            }
                            break;
                        }
                    }
                }
            }
            break;
    }
}

Vector3 SocialGroupSystem::calculateGroupCenter(const Group& group) {
    Vector3 center = {0.0f, 0.0f, 0.0f};
    if (group.members.empty()) return center;

    for (const auto& member : group.members) {
        Vector3 pos = ENTITY::GET_ENTITY_COORDS(member.pedHandle, true);
        center.x += pos.x;
        center.y += pos.y;
        center.z += pos.z;
    }

    float count = static_cast<float>(group.members.size());
    center.x /= count;
    center.y /= count;
    center.z /= count;

    return center;
}

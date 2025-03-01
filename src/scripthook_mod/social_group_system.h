#pragma once
#include "types.h"
#include <unordered_map>
#include <vector>
#include <string>

enum class GroupType {
    FAMILY,
    FRIENDS,
    GANG,
    WORKERS,
    SHOPKEEPERS,
    POLICE,
    CIVILIANS,
    CUSTOM
};

enum class GroupActivity {
    IDLE,
    PATROLLING,
    SOCIALIZING,
    WORKING,
    SHOPPING,
    PROTECTING,
    FOLLOWING_LEADER,
    CUSTOM_ACTIVITY
};

class SocialGroupSystem {
public:
    static SocialGroupSystem& getInstance() {
        static SocialGroupSystem instance;
        return instance;
    }

    struct GroupMember {
        Ped pedHandle;
        bool isLeader;
        float influence;
        Vector3 lastKnownPos;
        GroupActivity currentActivity;
    };

    struct Group {
        std::string groupId;
        GroupType type;
        std::vector<GroupMember> members;
        Vector3 baseLocation;
        float groupCohesion;        // 0.0 à 1.0
        float territorialRadius;    // Rayon de territoire du groupe
        GroupActivity currentActivity;
        std::vector<Vector3> territoryPoints;
    };

    // Gestion des groupes
    std::string createGroup(GroupType type, const Vector3& baseLocation);
    void addMemberToGroup(const std::string& groupId, Ped ped, bool isLeader = false);
    void removeFromGroup(const std::string& groupId, Ped ped);
    void updateGroups();
    
    // Activités de groupe
    void assignGroupActivity(const std::string& groupId, GroupActivity activity);
    void updateGroupActivities();
    void handleGroupConflicts();
    
    // Territoire
    void defineTerritory(const std::string& groupId, const std::vector<Vector3>& points);
    bool isInTerritory(const std::string& groupId, const Vector3& position);
    
    // Relations entre groupes
    void setGroupRelation(const std::string& group1, const std::string& group2, float relation);
    float getGroupRelation(const std::string& group1, const std::string& group2);

private:
    SocialGroupSystem() {}
    std::unordered_map<std::string, Group> groups;
    std::unordered_map<std::string, std::unordered_map<std::string, float>> groupRelations;
    
    void updateGroupCohesion(Group& group);
    void handleGroupFormation(Group& group);
    void updateGroupBehavior(Group& group);
    Vector3 calculateGroupCenter(const Group& group);
};

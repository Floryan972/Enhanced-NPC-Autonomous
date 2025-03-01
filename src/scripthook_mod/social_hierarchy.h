#pragma once
#include "types.h"
#include <unordered_map>
#include <vector>
#include <string>

enum class HierarchyRank {
    LEADER,
    ELDER,
    VETERAN,
    MEMBER,
    INITIATE,
    OUTSIDER
};

enum class SocialRole {
    MENTOR,
    GUARDIAN,
    TRADER,
    SCOUT,
    MEDIATOR,
    ENFORCER,
    HEALER,
    CRAFTSMAN
};

struct SocialPosition {
    HierarchyRank rank;
    std::vector<SocialRole> roles;
    float influence;
    float respect;
    int subordinates;
    std::vector<Ped> mentees;
};

class SocialHierarchy {
public:
    static SocialHierarchy& getInstance() {
        static SocialHierarchy instance;
        return instance;
    }

    struct HierarchyNode {
        Ped ped;
        HierarchyRank rank;
        std::vector<HierarchyNode*> subordinates;
        HierarchyNode* superior;
        float authority;
        std::vector<SocialRole> roles;
    };

    void initializeHierarchy(const std::string& groupId);
    void updateHierarchy();
    void promoteMember(Ped ped);
    void demoteMember(Ped ped);
    void assignRole(Ped ped, SocialRole role);
    void handlePowerStruggle(Ped challenger, Ped incumbent);
    
    // Nouvelles fonctions de hiérarchie
    void establishChainOfCommand(const std::string& groupId);
    void handleSuccession(const std::string& groupId, Ped oldLeader);
    void distributeResources(const std::string& groupId);
    void mediateConflict(Ped ped1, Ped ped2);

private:
    SocialHierarchy() {}
    std::unordered_map<std::string, std::vector<HierarchyNode>> groupHierarchies;
    std::unordered_map<Ped, SocialPosition> socialPositions;
    
    void updateAuthority(HierarchyNode* node);
    void resolveConflicts(const std::string& groupId);
    void balancePower(const std::string& groupId);
    float calculateInfluence(const SocialPosition& position);
};

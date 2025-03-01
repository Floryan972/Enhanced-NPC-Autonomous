#pragma once
#include "types.h"
#include <unordered_map>
#include <string>

enum class ReputationType {
    FRIENDLY,
    NEUTRAL,
    HOSTILE,
    FEARED,
    RESPECTED,
    CRIMINAL,
    HERO
};

enum class SocialStatus {
    OUTSIDER,
    MEMBER,
    RESPECTED,
    INFLUENTIAL,
    LEADER,
    LEGENDARY
};

class ReputationSystem {
public:
    static ReputationSystem& getInstance() {
        static ReputationSystem instance;
        return instance;
    }

    struct ReputationData {
        float reputation;         // -1.0 à 1.0
        float influence;          // 0.0 à 1.0
        float notoriety;         // 0.0 à 1.0
        ReputationType type;
        SocialStatus status;
        int crimesCommitted;
        int goodDeeds;
        std::unordered_map<std::string, float> groupReputation;  // réputation par groupe
    };

    void updateReputation(Ped ped, float delta);
    void recordCrime(Ped ped, float severity);
    void recordGoodDeed(Ped ped, float value);
    void updateSocialStatus(Ped ped);
    ReputationData* getReputation(Ped ped);
    void propagateReputation(Ped ped, float radius);
    float getGroupReputation(Ped ped, const std::string& groupId);
    void modifyGroupReputation(Ped ped, const std::string& groupId, float delta);

private:
    ReputationSystem() {}
    std::unordered_map<Ped, ReputationData> reputations;
    
    void calculateReputationType(ReputationData& data);
    void updateInfluence(Ped ped, ReputationData& data);
    void handleReputationEffects(Ped ped, ReputationData& data);
};

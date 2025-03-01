#pragma once
#include "types.h"
#include <unordered_map>
#include <vector>
#include <string>

enum class AllianceType {
    MARRIAGE,
    TRADE,
    MILITARY,
    CULTURAL,
    POLITICAL,
    PROTECTION
};

enum class AllianceStatus {
    PROPOSED,
    ACTIVE,
    STRAINED,
    BROKEN,
    RENEWED
};

struct AllianceTerms {
    std::vector<std::string> obligations;
    std::vector<std::string> benefits;
    float duration;
    float penalty;
    std::vector<Vector3> sharedTerritories;
};

struct Alliance {
    std::string allianceId;
    AllianceType type;
    AllianceStatus status;
    std::vector<std::string> memberFamilies;
    AllianceTerms terms;
    float strength;
    float trust;
    std::vector<std::string> sharedTraditions;
};

class AllianceSystem {
public:
    static AllianceSystem& getInstance() {
        static AllianceSystem instance;
        return instance;
    }

    void initializeAlliance(const std::string& family1, const std::string& family2, AllianceType type);
    void updateAlliances();
    void proposeAlliance(const std::string& proposer, const std::string& target, AllianceType type);
    void breakAlliance(const std::string& allianceId, const std::string& reason);
    
    // Nouvelles fonctions d'alliance
    void arrangeMarriage(const std::string& family1, const std::string& family2);
    void negotiateTerms(const std::string& allianceId, const AllianceTerms& terms);
    void handleAllianceEvent(const std::string& allianceId, const std::string& eventType);
    void shareTraditions(const std::string& allianceId);

private:
    AllianceSystem() {}
    std::unordered_map<std::string, Alliance> alliances;
    std::unordered_map<std::string, std::vector<std::string>> familyAlliances;
    
    void updateAllianceStrength(Alliance& alliance);
    void handleObligations(Alliance& alliance);
    void distributeResources(Alliance& alliance);
    void resolveConflicts(Alliance& alliance);
};

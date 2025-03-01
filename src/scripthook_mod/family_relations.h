#pragma once
#include "types.h"
#include <unordered_map>
#include <vector>
#include <string>

enum class RelationType {
    PARENT,
    CHILD,
    SIBLING,
    SPOUSE,
    EXTENDED_FAMILY,
    FRIEND,
    RIVAL
};

struct FamilyMember {
    Ped ped;
    RelationType relation;
    float closeness;
    float loyalty;
    std::vector<std::string> sharedMemories;
};

struct Family {
    std::string familyId;
    std::vector<FamilyMember> members;
    Vector3 homeLocation;
    float familyHonor;
    float stability;
    std::vector<std::string> traditions;
};

class FamilyRelations {
public:
    static FamilyRelations& getInstance() {
        static FamilyRelations instance;
        return instance;
    }

    void initializeFamily(const std::string& familyId);
    void updateFamilies();
    void addFamilyMember(const std::string& familyId, Ped ped, RelationType relation);
    void updateRelations(const std::string& familyId);
    void handleFamilyEvent(const std::string& familyId, const std::string& eventType);
    
    // Nouvelles fonctions familiales
    void organizeFamilyGathering(const std::string& familyId);
    void handleFamilyConflict(Ped ped1, Ped ped2);
    void passFamilyTradition(const std::string& familyId, const std::string& tradition);
    void updateFamilyHonor(const std::string& familyId, float delta);

private:
    FamilyRelations() {}
    std::unordered_map<std::string, Family> families;
    std::unordered_map<Ped, std::string> pedToFamily;
    
    void updateFamilyBonds(Family& family);
    void handleGenerationalChange(Family& family);
    void maintainTraditions(Family& family);
    void resolveInternalConflicts(Family& family);
};

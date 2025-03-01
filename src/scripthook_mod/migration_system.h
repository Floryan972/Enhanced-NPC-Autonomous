#pragma once
#include "types.h"
#include <unordered_map>
#include <vector>
#include <string>

enum class MigrationType {
    SEASONAL,
    RESOURCE_DRIVEN,
    CONFLICT_ESCAPE,
    OPPORTUNITY,
    FORCED
};

enum class TerrainType {
    PLAINS,
    FOREST,
    MOUNTAIN,
    URBAN,
    COASTAL,
    DESERT
};

struct MigrationPath {
    std::string pathId;
    std::vector<Vector3> waypoints;
    TerrainType terrain;
    float difficulty;
    float distance;
    bool isActive;
    std::vector<std::string> resourcesRequired;
};

struct Settlement {
    std::string settlementId;
    Vector3 location;
    TerrainType terrain;
    float capacity;
    float resources;
    std::vector<std::string> residentGroups;
    bool isSeasonal;
};

struct MigrationPlan {
    std::string planId;
    std::string groupId;
    MigrationType type;
    Settlement* origin;
    Settlement* destination;
    MigrationPath path;
    float progress;
    bool isActive;
    std::vector<std::string> participatingMembers;
};

class MigrationSystem {
public:
    static MigrationSystem& getInstance() {
        static MigrationSystem instance;
        return instance;
    }

    void initializeMigrationSystem();
    void updateMigration();
    void planMigration(const std::string& groupId, MigrationType type);
    void executeMigration(const std::string& planId);
    
    // Nouvelles fonctions de migration
    void createSettlement(const Vector3& location, TerrainType terrain);
    void updateSettlements();
    void handleSeasonalMigration();
    bool isLocationSuitable(const Vector3& location, const std::string& groupId);

private:
    MigrationSystem() {}
    std::unordered_map<std::string, MigrationPlan> activePlans;
    std::unordered_map<std::string, Settlement> settlements;
    std::unordered_map<std::string, std::vector<MigrationPath>> knownPaths;
    
    void updateMigrationPaths();
    void evaluateSettlementConditions();
    float calculatePathDifficulty(const MigrationPath& path);
    void handleMigrationEffects(const MigrationPlan& plan);
};

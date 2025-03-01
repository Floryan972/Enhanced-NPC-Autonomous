#pragma once
#include "types.h"
#include <unordered_map>
#include <vector>
#include <string>

enum class InteractionType {
    USE,
    HIDE,
    OBSERVE,
    GUARD,
    GATHER,
    MODIFY
};

struct InteractionPoint {
    Vector3 location;
    InteractionType type;
    float usefulness;
    int timesUsed;
    std::vector<std::string> compatibleBehaviors;
    bool isOccupied;
};

class EnvironmentInteraction {
public:
    static EnvironmentInteraction& getInstance() {
        static EnvironmentInteraction instance;
        return instance;
    }

    struct EnvironmentData {
        std::vector<InteractionPoint> interactionPoints;
        std::unordered_map<Vector3, float> dangerLevels;
        std::vector<Vector3> resourcePoints;
        std::unordered_map<Vector3, std::string> territoryMarkers;
        float environmentalThreat;
    };

    void discoverInteractionPoint(const Vector3& location, InteractionType type);
    void updateInteractionPoints();
    void handleEnvironmentChanges(const Vector3& location);
    void registerResourcePoint(const Vector3& location, const std::string& resourceType);
    void updateTerritoryControl(const std::string& groupId, const Vector3& location);
    
    // Nouvelles fonctions d'interaction
    void createEnvironmentalEvent(const Vector3& location, const std::string& eventType);
    void modifyEnvironment(const Vector3& location, const std::string& modificationType);
    void synchronizeWithWeather();
    InteractionPoint* findBestInteractionPoint(const Vector3& location, InteractionType type);

private:
    EnvironmentInteraction() {}
    std::unordered_map<std::string, EnvironmentData> environmentData;
    
    void updateDangerLevels();
    void cleanupUnusedPoints();
    void optimizeResourceDistribution();
    void handleTerrainChanges(const Vector3& location);
};

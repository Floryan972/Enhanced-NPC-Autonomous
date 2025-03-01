#pragma once
#include "types.h"
#include <vector>

enum class EnvironmentType {
    SAFE,
    DANGEROUS,
    COMBAT_ZONE,
    SOCIAL_AREA,
    RESTRICTED_AREA
};

class EnvironmentalSystem {
public:
    static EnvironmentalSystem& getInstance() {
        static EnvironmentalSystem instance;
        return instance;
    }

    struct EnvironmentalData {
        EnvironmentType type;
        float dangerLevel;
        float socialActivity;
        bool isIndoors;
        int nearbyNPCs;
        bool hasEscapeRoutes;
        Vector3 safeSpot;
    };

    void updateEnvironment(const Vector3& position);
    EnvironmentalData* getEnvironmentData(const Vector3& position);
    void handleWeatherEffects();
    void updateCoverPoints();
    Vector3 findNearestSafeSpot(const Vector3& position);

private:
    EnvironmentalSystem() {}
    std::vector<Vector3> coverPoints;
    std::vector<Vector3> safeSpots;
    
    float calculateDangerLevel(const Vector3& position);
    void scanForCoverPoints(const Vector3& center);
    bool isPositionSafe(const Vector3& position);
};

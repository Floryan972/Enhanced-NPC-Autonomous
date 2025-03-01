#pragma once
#include "types.h"
#include "personality_system.h"
#include "social_group_system.h"
#include "routine_system.h"
#include "event_manager.h"
#include "reputation_system.h"
#include "collective_memory.h"

class SystemCoordinator {
public:
    static SystemCoordinator& getInstance() {
        static SystemCoordinator instance;
        return instance;
    }

    void update();
    void handleWeatherChange(const std::string& weatherType);
    void handleCombatEvent(Ped attacker, Ped victim);
    void handleSocialInteraction(Ped ped1, Ped ped2, bool isPositive);
    void handleSpecialEvent(SpecialEventType eventType, const Vector3& location);
    void synchronizeSystems();

private:
    SystemCoordinator() {}
    
    void updateGroupDynamics();
    void updateEnvironmentalEffects();
    void handleSystemConflicts();
    void propagateSystemEffects();
    void cleanupInvalidEntities();
};

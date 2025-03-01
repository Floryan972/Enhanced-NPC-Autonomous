#pragma once
#include "types.h"
#include <vector>
#include <string>
#include <functional>

enum class SpecialEventType {
    RIOT,
    GANG_WAR,
    POLICE_RAID,
    CELEBRATION,
    EMERGENCY,
    PROTEST,
    FESTIVAL,
    NATURAL_DISASTER
};

struct EventTrigger {
    float probability;
    std::function<bool()> condition;
    Vector3 location;
    float radius;
};

class EventManager {
public:
    static EventManager& getInstance() {
        static EventManager instance;
        return instance;
    }

    struct ActiveEvent {
        SpecialEventType type;
        Vector3 epicenter;
        float radius;
        float intensity;
        float duration;
        float timeRemaining;
        bool isActive;
    };

    void updateEvents();
    void triggerEvent(SpecialEventType type, const Vector3& location, float radius);
    void registerEventTrigger(SpecialEventType type, const EventTrigger& trigger);
    void handleEventEffects(const ActiveEvent& event);
    bool isLocationAffectedByEvent(const Vector3& location, SpecialEventType type);
    void cleanupEvents();

private:
    EventManager() {}
    std::vector<ActiveEvent> activeEvents;
    std::unordered_map<SpecialEventType, std::vector<EventTrigger>> eventTriggers;
    
    void applyEventEffects(const ActiveEvent& event);
    void updateNPCBehavior(Ped ped, const ActiveEvent& event);
    void spawnEventProps(const ActiveEvent& event);
    void createEventAmbience(const ActiveEvent& event);
};

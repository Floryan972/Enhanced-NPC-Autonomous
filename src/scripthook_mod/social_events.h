#pragma once
#include "types.h"
#include <unordered_map>
#include <vector>
#include <string>

enum class SocialEventType {
    WEDDING,
    CORONATION,
    FUNERAL,
    FESTIVAL,
    TOURNAMENT,
    FEAST,
    PILGRIMAGE,
    COUNCIL
};

struct EventRequirement {
    std::vector<std::string> requiredRoles;
    std::vector<std::string> requiredItems;
    float minimumHonor;
    int minimumParticipants;
    bool requiresAlliance;
};

struct SocialEvent {
    SocialEventType type;
    std::string eventId;
    std::vector<std::string> participatingGroups;
    EventRequirement requirements;
    Vector3 location;
    float duration;
    float importance;
    bool isActive;
    std::vector<Ritual> associatedRituals;
};

class SocialEvents {
public:
    static SocialEvents& getInstance() {
        static SocialEvents instance;
        return instance;
    }

    void initializeEvent(SocialEventType type, const std::vector<std::string>& groups);
    void updateEvents();
    void startEvent(const std::string& eventId);
    void endEvent(const std::string& eventId);
    void addParticipant(const std::string& eventId, const std::string& groupId);
    
    // Nouvelles fonctions d'événements
    void createCustomEvent(const std::string& eventId, const SocialEvent& event);
    void handleEventOutcome(const std::string& eventId);
    void synchronizeWithTraditions(const std::string& eventId);
    bool canGroupParticipate(const std::string& groupId, const std::string& eventId);

private:
    SocialEvents() {}
    std::unordered_map<std::string, SocialEvent> activeEvents;
    std::unordered_map<std::string, std::vector<std::string>> groupEvents;
    
    void setupEventLocation(SocialEvent& event);
    void createEventRituals(SocialEvent& event);
    void distributeRoles(SocialEvent& event);
    void handleEventConflicts(SocialEvent& event);
};

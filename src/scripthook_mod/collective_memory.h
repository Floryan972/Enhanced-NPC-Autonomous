#pragma once
#include "types.h"
#include <unordered_map>
#include <vector>
#include <string>

enum class MemoryType {
    POSITIVE,
    NEGATIVE,
    NEUTRAL,
    THREAT,
    ALLIANCE
};

struct CollectiveMemoryEvent {
    MemoryType type;
    Vector3 location;
    float importance;    // 0.0 à 1.0
    float timeStamp;
    std::string description;
    Ped mainActor;
    std::vector<Ped> involvedPeds;
};

class CollectiveMemory {
public:
    static CollectiveMemory& getInstance() {
        static CollectiveMemory instance;
        return instance;
    }

    struct GroupMemory {
        std::vector<CollectiveMemoryEvent> events;
        std::unordered_map<Ped, float> knownActors;     // Ped et leur importance
        std::vector<Vector3> significantLocations;
        float groupTension;        // 0.0 à 1.0
        std::unordered_map<std::string, float> groupRelations;  // Relations avec d'autres groupes
    };

    void recordEvent(const std::string& groupId, const CollectiveMemoryEvent& event);
    void updateMemories();
    void shareMemories(const std::string& sourceGroup, const std::string& targetGroup);
    std::vector<CollectiveMemoryEvent> getRelevantMemories(const std::string& groupId, const Vector3& location);
    void forgetOldMemories(float maxAge);
    float calculateThreatLevel(const std::string& groupId, const Vector3& location);
    
    // Nouvelles fonctions pour la météo et les événements
    void recordWeatherEvent(const Vector3& location, const std::string& weatherType);
    bool shouldReactToWeather(const std::string& groupId, const Vector3& location);
    void updateWeatherBehavior(const std::string& groupId);

private:
    CollectiveMemory() {}
    std::unordered_map<std::string, GroupMemory> groupMemories;
    std::vector<CollectiveMemoryEvent> weatherEvents;
    
    void propagateMemory(const CollectiveMemoryEvent& event);
    void updateGroupTension(const std::string& groupId);
    float calculateEventRelevance(const CollectiveMemoryEvent& event, const Vector3& location);
    void mergeMemories(GroupMemory& target, const GroupMemory& source);
};

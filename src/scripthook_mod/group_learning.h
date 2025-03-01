#pragma once
#include "types.h"
#include <unordered_map>
#include <vector>
#include <string>

enum class LearningCategory {
    COMBAT,
    SOCIAL,
    SURVIVAL,
    TERRITORY,
    RESOURCES,
    TACTICS
};

struct LearnedBehavior {
    LearningCategory category;
    float successRate;
    int timesUsed;
    float effectiveness;
    Vector3 lastLocation;
    std::vector<Ped> teachingPeds;
};

struct GroupKnowledge {
    std::unordered_map<std::string, LearnedBehavior> behaviors;
    std::vector<Vector3> strategicLocations;
    std::unordered_map<Ped, float> teacherRatings;
    float adaptabilityScore;
    int generationCount;
};

class GroupLearning {
public:
    static GroupLearning& getInstance() {
        static GroupLearning instance;
        return instance;
    }

    void initializeGroupLearning(const std::string& groupId);
    void recordBehaviorOutcome(const std::string& groupId, const std::string& behaviorId, bool success);
    void shareBehavior(const std::string& sourceGroup, const std::string& targetGroup, const std::string& behaviorId);
    void updateGroupKnowledge();
    void teachBehavior(Ped teacher, Ped student, const std::string& behaviorId);
    void adaptToEnvironment(const std::string& groupId, const Vector3& location);
    
    // Nouvelles fonctions d'apprentissage avancé
    void evolveTactics(const std::string& groupId);
    void learnFromEvents(const std::string& groupId, const CollectiveMemoryEvent& event);
    void optimizeBehaviors(const std::string& groupId);
    float evaluateStrategyEffectiveness(const std::string& groupId, const std::string& strategyId);

private:
    GroupLearning() {}
    std::unordered_map<std::string, GroupKnowledge> groupKnowledge;
    
    void updateTeacherRatings(const std::string& groupId);
    void pruneIneffectiveBehaviors(const std::string& groupId);
    void generateNewStrategies(const std::string& groupId);
    void adaptBehaviorToWeather(LearnedBehavior& behavior, const std::string& weatherType);
};

#pragma once
#include "types.h"
#include <unordered_map>
#include <vector>
#include <string>

enum class RitualType {
    INITIATION,
    CELEBRATION,
    MOURNING,
    GATHERING,
    TRAINING,
    CEREMONY
};

struct RitualPhase {
    std::string name;
    float duration;
    std::vector<std::string> animations;
    std::vector<Vector3> positions;
    bool requiresLeader;
};

struct Ritual {
    RitualType type;
    std::vector<RitualPhase> phases;
    float importance;
    std::vector<Ped> participants;
    Vector3 location;
    bool isActive;
    int currentPhase;
    float timeRemaining;
};

class GroupRituals {
public:
    static GroupRituals& getInstance() {
        static GroupRituals instance;
        return instance;
    }

    void initializeRituals(const std::string& groupId);
    void updateRituals();
    void startRitual(const std::string& groupId, RitualType type);
    void endRitual(const std::string& groupId, const std::string& ritualId);
    void addParticipant(const std::string& ritualId, Ped ped);
    
    // Nouvelles fonctions de rituels
    void createCustomRitual(const std::string& groupId, const std::vector<RitualPhase>& phases);
    void handleRitualOutcome(const std::string& ritualId, bool success);
    void synchronizeWithWeather(const std::string& ritualId);
    bool isParticipatingInRitual(Ped ped);

private:
    GroupRituals() {}
    std::unordered_map<std::string, std::vector<Ritual>> groupRituals;
    std::unordered_map<std::string, Ritual> activeRituals;
    
    void updateRitualPhase(Ritual& ritual);
    void positionParticipants(Ritual& ritual);
    void createRitualEffects(const Ritual& ritual);
    void recordRitualMemory(const std::string& groupId, const Ritual& ritual);
};

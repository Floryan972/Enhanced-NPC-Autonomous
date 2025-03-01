#pragma once
#include "types.h"
#include <unordered_map>

enum class PersonalityType {
    AGGRESSIVE,    // Combatif et territorial
    CAUTIOUS,      // Prudent et évite les conflits
    FRIENDLY,      // Social et coopératif
    NEUTRAL,       // Comportement standard
    FEARFUL,       // Tendance à fuir
    CURIOUS,       // Explore et investigue
    PROTECTIVE,    // Protège les autres NPCs
    LEADER,        // Influence les autres NPCs
};

enum class EmotionalState {
    CALM,
    ANGRY,
    SCARED,
    SUSPICIOUS,
    HAPPY,
    NERVOUS
};

class PersonalitySystem {
public:
    static PersonalitySystem& getInstance() {
        static PersonalitySystem instance;
        return instance;
    }

    struct PersonalityTraits {
        PersonalityType type;
        EmotionalState currentEmotion;
        float bravery;          // 0.0 à 1.0
        float sociability;      // 0.0 à 1.0
        float aggression;       // 0.0 à 1.0
        float intelligence;     // 0.0 à 1.0
        float leadership;       // 0.0 à 1.0
        int groupInfluence;     // Rayon d'influence sur les autres NPCs
    };

    void initializePersonality(Ped ped);
    void updateEmotionalState(Ped ped);
    void influenceNearbyNPCs(Ped ped);
    PersonalityTraits* getPersonality(Ped ped);
    void handleEnvironmentalInfluence(Ped ped, const Vector3& position);

private:
    PersonalitySystem() {}
    std::unordered_map<Ped, PersonalityTraits> personalities;
    
    void updateGroupDynamics(Ped ped);
    float calculateEnvironmentalStress(const Vector3& position);
};

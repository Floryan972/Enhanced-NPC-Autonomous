#pragma once
#include "types.h"

enum class NPCState {
    IDLE,
    ALERT,
    SUSPICIOUS,
    COMBAT,
    FLEE,
    INVESTIGATE,
    SOCIAL
};

class NPCStateManager {
public:
    static NPCStateManager& getInstance() {
        static NPCStateManager instance;
        return instance;
    }

    void updateState(Ped ped);
    NPCState getCurrentState(Ped ped);
    void setState(Ped ped, NPCState state);
    void handleStateTransition(Ped ped, NPCState oldState, NPCState newState);

private:
    NPCStateManager() {}
    std::unordered_map<Ped, NPCState> npcStates;
    
    bool shouldTransitionToAlert(Ped ped);
    bool shouldTransitionToCombat(Ped ped);
    bool shouldTransitionToFlee(Ped ped);
    void executeStateAction(Ped ped, NPCState state);
};

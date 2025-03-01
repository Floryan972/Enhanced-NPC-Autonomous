#include "npc_state.h"
#include "memory_manager.h"
#include "natives.h"

void NPCStateManager::updateState(Ped ped) {
    NPCState currentState = getCurrentState(ped);
    NPCState newState = currentState;

    // Vérifier les transitions possibles
    if (shouldTransitionToAlert(ped)) {
        newState = NPCState::ALERT;
    } else if (shouldTransitionToCombat(ped)) {
        newState = NPCState::COMBAT;
    } else if (shouldTransitionToFlee(ped)) {
        newState = NPCState::FLEE;
    }

    // Si l'état a changé, gérer la transition
    if (newState != currentState) {
        handleStateTransition(ped, currentState, newState);
        setState(ped, newState);
    }

    // Exécuter les actions de l'état actuel
    executeStateAction(ped, getCurrentState(ped));
}

NPCState NPCStateManager::getCurrentState(Ped ped) {
    auto it = npcStates.find(ped);
    if (it != npcStates.end()) {
        return it->second;
    }
    return NPCState::IDLE;
}

void NPCStateManager::setState(Ped ped, NPCState state) {
    npcStates[ped] = state;
}

bool NPCStateManager::shouldTransitionToAlert(Ped ped) {
    auto* memory = MemoryManager::getInstance().getNPCMemory(ped);
    if (!memory) return false;

    // Vérifier les conditions d'alerte
    return memory->threatLevel > 0.3f || 
           memory->hasSeenPlayer || 
           ENTITY::HAS_ENTITY_CLEAR_LOS_TO_ENTITY(ped, PLAYER::PLAYER_PED_ID(), 17);
}

bool NPCStateManager::shouldTransitionToCombat(Ped ped) {
    auto* memory = MemoryManager::getInstance().getNPCMemory(ped);
    if (!memory) return false;

    // Vérifier les conditions de combat
    return memory->threatLevel > 0.7f || 
           PED::IS_PED_IN_COMBAT(ped, PLAYER::PLAYER_PED_ID()) ||
           ENTITY::HAS_ENTITY_BEEN_DAMAGED_BY_ENTITY(ped, PLAYER::PLAYER_PED_ID(), 1);
}

bool NPCStateManager::shouldTransitionToFlee(Ped ped) {
    auto* memory = MemoryManager::getInstance().getNPCMemory(ped);
    if (!memory) return false;

    // Vérifier les conditions de fuite
    return PED::GET_PED_HEALTH(ped) < 50 || 
           memory->threatLevel > 0.9f ||
           WEAPON::IS_PED_ARMED(PLAYER::PLAYER_PED_ID(), 7);
}

void NPCStateManager::handleStateTransition(Ped ped, NPCState oldState, NPCState newState) {
    // Nettoyer l'ancien état
    AI::CLEAR_PED_TASKS(ped);

    // Configurer le nouveau état
    switch (newState) {
        case NPCState::ALERT:
            PED::SET_PED_ALERTNESS(ped, 2);
            PED::SET_PED_COMBAT_ATTRIBUTES(ped, 46, true);
            break;
        case NPCState::COMBAT:
            PED::SET_PED_COMBAT_ABILITY(ped, 100);
            PED::SET_PED_COMBAT_MOVEMENT(ped, 2);
            break;
        case NPCState::FLEE:
            PED::SET_PED_FLEE_ATTRIBUTES(ped, 2, true);
            break;
    }
}

void NPCStateManager::executeStateAction(Ped ped, NPCState state) {
    Vector3 playerPos = ENTITY::GET_ENTITY_COORDS(PLAYER::PLAYER_PED_ID(), true);
    Vector3 pedPos = ENTITY::GET_ENTITY_COORDS(ped, true);

    switch (state) {
        case NPCState::ALERT:
            AI::TASK_TURN_PED_TO_FACE_COORD(ped, playerPos.x, playerPos.y, playerPos.z, 0);
            break;
        case NPCState::COMBAT:
            AI::TASK_COMBAT_PED(ped, PLAYER::PLAYER_PED_ID(), 0, 16);
            break;
        case NPCState::FLEE:
            AI::TASK_SMART_FLEE_PED(ped, PLAYER::PLAYER_PED_ID(), 100.0f, -1, false, false);
            break;
        case NPCState::INVESTIGATE:
            AI::TASK_GO_TO_COORD_ANY_MEANS(ped, playerPos.x, playerPos.y, playerPos.z, 2.0f, 0, 0, 786603, 0xbf800000);
            break;
    }
}

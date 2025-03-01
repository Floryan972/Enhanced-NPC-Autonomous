#include "npc_controller.h"
#include "natives.h"
#include <algorithm>

void NPCController::update() {
    // Obtenir tous les peds dans la zone
    const int MAX_PEDS = 1024;
    Ped peds[MAX_PEDS];
    int count = worldGetAllPeds(peds, MAX_PEDS);

    for (int i = 0; i < count; i++) {
        Ped ped = peds[i];
        if (ENTITY::DOES_ENTITY_EXIST(ped) && !ENTITY::IS_ENTITY_DEAD(ped) && !PED::IS_PED_A_PLAYER(ped)) {
            if (!isNPCEnhanced(ped)) {
                enhanceNPCBehavior(ped);
            }
            updateNPCAwareness(ped);
            updateNPCBehavior(ped);
        }
    }
}

void NPCController::enhanceNPCBehavior(Ped ped) {
    // Améliorer les capacités du NPC
    PED::SET_PED_COMBAT_ABILITY(ped, 100);
    PED::SET_PED_COMBAT_MOVEMENT(ped, 2);
    PED::SET_PED_COMBAT_RANGE(ped, 2);
    
    // Ajouter à la liste des NPCs améliorés
    enhancedNPCs.push_back(ped);
}

bool NPCController::isNPCEnhanced(Ped ped) {
    return std::find(enhancedNPCs.begin(), enhancedNPCs.end(), ped) != enhancedNPCs.end();
}

void NPCController::updateNPCAwareness(Ped ped) {
    Vector3 pedPos = ENTITY::GET_ENTITY_COORDS(ped, true);
    Vector3 playerPos = ENTITY::GET_ENTITY_COORDS(PLAYER::PLAYER_PED_ID(), true);
    
    float distance = SYSTEM::VDIST(pedPos.x, pedPos.y, pedPos.z, playerPos.x, playerPos.y, playerPos.z);
    
    if (distance < 50.0f) {
        // Le NPC devient plus attentif quand le joueur est proche
        PED::SET_PED_ALERTNESS(ped, 3);
        PED::SET_PED_HEARING_RANGE(ped, 100.0f);
        PED::SET_PED_SEEING_RANGE(ped, 100.0f);
    }
}

void NPCController::updateNPCBehavior(Ped ped) {
    // Vérifier si le NPC est en situation de combat
    if (PED::IS_PED_IN_COMBAT(ped, PLAYER::PLAYER_PED_ID())) {
        handleCombatSituation(ped);
    } else {
        handleSocialSituation(ped);
    }
}

void NPCController::handleCombatSituation(Ped ped) {
    // Comportement amélioré en combat
    PED::SET_PED_COMBAT_ABILITY(ped, 100);
    PED::SET_PED_COMBAT_ATTRIBUTES(ped, 46, true);
    AI::TASK_COMBAT_PED(ped, PLAYER::PLAYER_PED_ID(), 0, 16);
}

void NPCController::handleSocialSituation(Ped ped) {
    // Comportement social amélioré
    Vector3 pedPos = ENTITY::GET_ENTITY_COORDS(ped, true);
    Vector3 playerPos = ENTITY::GET_ENTITY_COORDS(PLAYER::PLAYER_PED_ID(), true);
    
    float distance = SYSTEM::VDIST(pedPos.x, pedPos.y, pedPos.z, playerPos.x, playerPos.y, playerPos.z);
    
    if (distance < 20.0f) {
        // Réagir à la présence du joueur de manière plus naturelle
        int scenario = rand() % 3;
        switch (scenario) {
            case 0:
                AI::TASK_TURN_PED_TO_FACE_ENTITY(ped, PLAYER::PLAYER_PED_ID(), 1000);
                break;
            case 1:
                AI::TASK_START_SCENARIO_IN_PLACE(ped, "WORLD_HUMAN_STAND_IMPATIENT", 0, true);
                break;
            case 2:
                AI::TASK_SMART_FLEE_PED(ped, PLAYER::PLAYER_PED_ID(), 100.0f, -1, false, false);
                break;
        }
    }
}

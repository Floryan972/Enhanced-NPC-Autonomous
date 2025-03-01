#include "script.h"
#include "npc_controller.h"
#include "natives.h"
#include <windows.h>

void ScriptMain() {
    // Initialisation
    NPCController& controller = NPCController::getInstance();
    
    // Boucle principale du script
    while (true) {
        controller.update();
        WAIT(0);
    }
}

void ScriptInit() {
    // Code d'initialisation si nécessaire
}

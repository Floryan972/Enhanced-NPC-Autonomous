#include <natives.h>
#include <types.h>
#include <main.h>
#include <script.h>

void ScriptMain() {
    while (true) {
        // Obtenir tous les peds (NPCs) dans la zone
        const int ARR_SIZE = 1024;
        Ped peds[ARR_SIZE];
        int count = worldGetAllPeds(peds, ARR_SIZE);

        // Traiter chaque NPC
        for (int i = 0; i < count; i++) {
            Ped ped = peds[i];
            if (ENTITY::DOES_ENTITY_EXIST(ped) && !ENTITY::IS_ENTITY_DEAD(ped) && !PED::IS_PED_A_PLAYER(ped)) {
                // Vérifier si le NPC est dans une zone d'intérêt
                Vector3 pedPos = ENTITY::GET_ENTITY_COORDS(ped, true);
                Vector3 playerPos = ENTITY::GET_ENTITY_COORDS(PLAYER::PLAYER_PED_ID(), true);
                
                // Si le NPC est proche du joueur (dans un rayon de 100 unités)
                if (SYSTEM::VDIST(pedPos.x, pedPos.y, pedPos.z, playerPos.x, playerPos.y, playerPos.z) < 100.0f) {
                    // Améliorer le comportement du NPC
                    AI::TASK_SMART_FLEE_PED(ped, PLAYER::PLAYER_PED_ID(), 100.0f, -1, false, false);
                }
            }
        }

        WAIT(0);
    }
}

void ScriptInit() {
    // Initialisation du script
    main();
}

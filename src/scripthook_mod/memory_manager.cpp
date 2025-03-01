#include "memory_manager.h"
#include "natives.h"
#include <windows.h>

void MemoryManager::updateNPCMemory(Ped ped, const Vector3& playerPos) {
    auto& memory = npcMemories[ped];
    
    // Mettre à jour la dernière position connue du joueur
    memory.lastKnownPlayerPos = playerPos;
    memory.lastInteractionTime = GetTickCount();
    
    // Vérifier si le NPC peut voir le joueur
    if (ENTITY::HAS_ENTITY_CLEAR_LOS_TO_ENTITY(ped, PLAYER::PLAYER_PED_ID(), 17)) {
        memory.hasSeenPlayer = true;
        
        // Ajuster le niveau de menace
        if (WEAPON::IS_PED_ARMED(PLAYER::PLAYER_PED_ID(), 7)) {
            memory.threatLevel = std::min(memory.threatLevel + 0.2f, 1.0f);
        } else {
            memory.threatLevel = std::max(memory.threatLevel - 0.1f, 0.0f);
        }
    }
}

MemoryManager::NPCMemory* MemoryManager::getNPCMemory(Ped ped) {
    auto it = npcMemories.find(ped);
    if (it != npcMemories.end()) {
        return &it->second;
    }
    
    // Créer une nouvelle mémoire si elle n'existe pas
    NPCMemory& memory = npcMemories[ped];
    memory.hasSeenPlayer = false;
    memory.threatLevel = 0.0f;
    memory.combatStyle = rand() % 3;  // Style de combat aléatoire
    memory.personalityType = rand() % 5;  // Personnalité aléatoire
    
    return &memory;
}

void MemoryManager::clearMemory(Ped ped) {
    npcMemories.erase(ped);
}

void MemoryManager::cleanup() {
    // Nettoyer les NPCs qui n'existent plus
    for (auto it = npcMemories.begin(); it != npcMemories.end();) {
        if (!ENTITY::DOES_ENTITY_EXIST(it->first)) {
            it = npcMemories.erase(it);
        } else {
            ++it;
        }
    }
}

#pragma once
#include <unordered_map>
#include "types.h"

class MemoryManager {
public:
    static MemoryManager& getInstance() {
        static MemoryManager instance;
        return instance;
    }

    // Stockage de la mémoire des NPCs
    struct NPCMemory {
        Vector3 lastKnownPlayerPos;
        DWORD lastInteractionTime;
        bool hasSeenPlayer;
        float threatLevel;
        int combatStyle;
        int personalityType;
    };

    void updateNPCMemory(Ped ped, const Vector3& playerPos);
    NPCMemory* getNPCMemory(Ped ped);
    void clearMemory(Ped ped);
    void cleanup();

private:
    MemoryManager() {}
    std::unordered_map<Ped, NPCMemory> npcMemories;
};

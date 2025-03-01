#pragma once
#include "types.h"
#include <vector>

class NPCController {
public:
    static NPCController& getInstance() {
        static NPCController instance;
        return instance;
    }

    void update();
    void enhanceNPCBehavior(Ped ped);
    bool isNPCEnhanced(Ped ped);

private:
    NPCController() {}
    std::vector<Ped> enhancedNPCs;
    
    void updateNPCAwareness(Ped ped);
    void updateNPCBehavior(Ped ped);
    void handleCombatSituation(Ped ped);
    void handleSocialSituation(Ped ped);
};

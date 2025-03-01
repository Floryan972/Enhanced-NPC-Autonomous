#pragma once
#include <vector>
#include <functional>
#include "types.h"

enum class GameEvent {
    PLAYER_SPOTTED,
    GUNSHOT_HEARD,
    COMBAT_STARTED,
    COMBAT_ENDED,
    PLAYER_ENTERED_VEHICLE,
    PLAYER_LEFT_VEHICLE,
    NPC_DAMAGED,
    NPC_KILLED
};

struct EventData {
    GameEvent type;
    Ped sourcePed;
    Ped targetPed;
    Vector3 location;
    float intensity;
};

class EventSystem {
public:
    static EventSystem& getInstance() {
        static EventSystem instance;
        return instance;
    }

    using EventCallback = std::function<void(const EventData&)>;
    
    void registerCallback(GameEvent event, EventCallback callback);
    void triggerEvent(const EventData& eventData);
    void update();

private:
    EventSystem() {}
    struct EventListener {
        GameEvent event;
        EventCallback callback;
    };
    
    std::vector<EventListener> listeners;
    std::vector<EventData> eventQueue;
};

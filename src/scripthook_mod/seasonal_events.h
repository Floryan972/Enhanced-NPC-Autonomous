#pragma once
#include "types.h"
#include <unordered_map>
#include <vector>
#include <string>

enum class Season {
    SPRING,
    SUMMER,
    AUTUMN,
    WINTER
};

enum class SeasonalEventType {
    HARVEST_FESTIVAL,
    WINTER_SOLSTICE,
    SPRING_CELEBRATION,
    SUMMER_GAMES,
    AUTUMN_FEAST,
    NEW_YEAR
};

struct SeasonalRequirement {
    Season season;
    float minTemperature;
    float maxTemperature;
    bool requiresDaylight;
    bool requiresNight;
    std::vector<std::string> requiredResources;
};

struct SeasonalEvent {
    SeasonalEventType type;
    std::string eventId;
    SeasonalRequirement requirements;
    std::vector<std::string> participatingGroups;
    Vector3 location;
    float duration;
    bool isActive;
    std::vector<Ritual> seasonalRituals;
    std::vector<std::string> seasonalTraditions;
};

class SeasonalEvents {
public:
    static SeasonalEvents& getInstance() {
        static SeasonalEvents instance;
        return instance;
    }

    void initializeSeasonalEvent(SeasonalEventType type);
    void updateSeasonalEvents();
    void startSeasonalEvent(const std::string& eventId);
    void endSeasonalEvent(const std::string& eventId);
    
    // Nouvelles fonctions saisonnières
    void updateSeason();
    void createCustomSeasonalEvent(const SeasonalEvent& event);
    void handleSeasonalOutcome(const std::string& eventId);
    void synchronizeWithWeather(const std::string& eventId);

private:
    SeasonalEvents() {}
    Season currentSeason;
    std::unordered_map<std::string, SeasonalEvent> activeEvents;
    std::vector<std::string> upcomingEvents;
    
    void setupSeasonalLocation(SeasonalEvent& event);
    void createSeasonalRituals(SeasonalEvent& event);
    void distributeSeasonalRoles(SeasonalEvent& event);
    void handleWeatherEffects(SeasonalEvent& event);
};

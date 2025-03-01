#include "seasonal_events.h"
#include "natives.h"
#include "alliance_system.h"
#include "family_relations.h"
#include "group_rituals.h"
#include "collective_memory.h"

void SeasonalEvents::initializeSeasonalEvent(SeasonalEventType type) {
    std::string eventId = "seasonal_" + std::to_string(MISC::GET_GAME_TIMER());
    
    SeasonalEvent event;
    event.type = type;
    event.eventId = eventId;
    event.isActive = false;
    
    // Configurer selon le type
    switch (type) {
        case SeasonalEventType::HARVEST_FESTIVAL:
        {
            event.requirements.season = Season::AUTUMN;
            event.requirements.requiresDaylight = true;
            event.requirements.minTemperature = 10.0f;
            event.requirements.maxTemperature = 25.0f;
            event.duration = 7200.0f; // 2 heures
            
            // Traditions spécifiques
            event.seasonalTraditions = {
                "harvest_dance",
                "crop_blessing",
                "community_feast"
            };
            break;
        }
        
        case SeasonalEventType::WINTER_SOLSTICE:
        {
            event.requirements.season = Season::WINTER;
            event.requirements.requiresNight = true;
            event.requirements.minTemperature = -10.0f;
            event.requirements.maxTemperature = 5.0f;
            event.duration = 3600.0f; // 1 heure
            
            event.seasonalTraditions = {
                "light_ceremony",
                "gift_exchange",
                "winter_tales"
            };
            break;
        }
    }
    
    // Configurer l'emplacement
    setupSeasonalLocation(event);
    
    // Créer les rituels saisonniers
    createSeasonalRituals(event);
    
    activeEvents[eventId] = event;
}

void SeasonalEvents::updateSeason() {
    // Obtenir l'heure du jeu
    int hours, minutes;
    CLOCK::GET_POSIX_TIME(&hours, &minutes);
    
    // Obtenir la météo
    Hash weatherHash;
    MISC::GET_CURR_WEATHER_STATE(&weatherHash);
    
    // Déterminer la saison
    Season newSeason;
    if (weatherHash == MISC::GET_HASH_KEY("XMAS")) {
        newSeason = Season::WINTER;
    } else if (weatherHash == MISC::GET_HASH_KEY("RAIN") || 
               weatherHash == MISC::GET_HASH_KEY("THUNDER")) {
        newSeason = Season::SPRING;
    } else if (weatherHash == MISC::GET_HASH_KEY("CLEAR") || 
               weatherHash == MISC::GET_HASH_KEY("EXTRASUNNY")) {
        newSeason = Season::SUMMER;
    } else {
        newSeason = Season::AUTUMN;
    }
    
    // Si la saison change
    if (newSeason != currentSeason) {
        currentSeason = newSeason;
        handleSeasonChange();
    }
}

void SeasonalEvents::setupSeasonalLocation(SeasonalEvent& event) {
    Vector3 bestLocation;
    float bestScore = -1.0f;
    
    // Trouver le meilleur emplacement selon la saison
    switch (event.requirements.season) {
        case Season::SPRING:
            // Chercher des zones vertes
            for (int i = 0; i < 10; i++) {
                Vector3 testLoc = {
                    MISC::GET_RANDOM_FLOAT_IN_RANGE(-1000.0f, 1000.0f),
                    MISC::GET_RANDOM_FLOAT_IN_RANGE(-1000.0f, 1000.0f),
                    0.0f
                };
                
                if (MISC::GET_GROUND_Z_FOR_3D_COORD(
                    testLoc.x, testLoc.y, 1000.0f,
                    &testLoc.z, false
                )) {
                    float score = 0.0f;
                    
                    // Vérifier la végétation
                    if (MISC::GET_HASH_KEY("GRASS") == 
                        OBJECT::GET_HASH_KEY_OF_MAP_OBJECT_AT_COORDS(
                            testLoc.x, testLoc.y, testLoc.z
                        )) {
                        score += 0.5f;
                    }
                    
                    if (score > bestScore) {
                        bestScore = score;
                        bestLocation = testLoc;
                    }
                }
            }
            break;
            
        case Season::WINTER:
            // Chercher des zones élevées
            for (int i = 0; i < 10; i++) {
                Vector3 testLoc = {
                    MISC::GET_RANDOM_FLOAT_IN_RANGE(-1000.0f, 1000.0f),
                    MISC::GET_RANDOM_FLOAT_IN_RANGE(-1000.0f, 1000.0f),
                    0.0f
                };
                
                if (MISC::GET_GROUND_Z_FOR_3D_COORD(
                    testLoc.x, testLoc.y, 1000.0f,
                    &testLoc.z, false
                )) {
                    float score = testLoc.z / 1000.0f;
                    
                    if (score > bestScore) {
                        bestScore = score;
                        bestLocation = testLoc;
                    }
                }
            }
            break;
    }
    
    event.location = bestLocation;
}

void SeasonalEvents::createSeasonalRituals(SeasonalEvent& event) {
    switch (event.type) {
        case SeasonalEventType::HARVEST_FESTIVAL:
        {
            // Rituel de bénédiction des récoltes
            Ritual blessing;
            blessing.type = RitualType::CEREMONY;
            blessing.importance = 0.9f;
            
            RitualPhase gathering;
            gathering.name = "harvest_gathering";
            gathering.duration = 300.0f;
            gathering.animations = {"WORLD_HUMAN_GUARD_PATROL"};
            
            RitualPhase blessing_phase;
            blessing_phase.name = "crop_blessing";
            blessing_phase.duration = 180.0f;
            blessing_phase.animations = {"WORLD_HUMAN_GUARD_STAND"};
            
            blessing.phases = {gathering, blessing_phase};
            event.seasonalRituals.push_back(blessing);
            
            // Rituel de festin communautaire
            Ritual feast;
            feast.type = RitualType::CELEBRATION;
            feast.importance = 0.8f;
            
            RitualPhase preparation;
            preparation.name = "feast_preparation";
            preparation.duration = 600.0f;
            preparation.animations = {"WORLD_HUMAN_SEAT_WALL_EATING"};
            
            feast.phases = {preparation};
            event.seasonalRituals.push_back(feast);
            break;
        }
        
        case SeasonalEventType::WINTER_SOLSTICE:
        {
            // Rituel des lumières
            Ritual lights;
            lights.type = RitualType::CEREMONY;
            lights.importance = 1.0f;
            
            RitualPhase procession;
            procession.name = "light_procession";
            procession.duration = 300.0f;
            procession.animations = {"WORLD_HUMAN_GUARD_PATROL"};
            procession.requiresNight = true;
            
            lights.phases = {procession};
            event.seasonalRituals.push_back(lights);
            break;
        }
    }
}

void SeasonalEvents::handleWeatherEffects(SeasonalEvent& event) {
    // Obtenir la météo actuelle
    Hash weatherHash;
    MISC::GET_CURR_WEATHER_STATE(&weatherHash);
    
    // Vérifier la compatibilité avec l'événement
    bool weatherCompatible = true;
    
    switch (event.requirements.season) {
        case Season::WINTER:
            if (weatherHash != MISC::GET_HASH_KEY("XMAS") &&
                weatherHash != MISC::GET_HASH_KEY("SNOW")) {
                weatherCompatible = false;
            }
            break;
            
        case Season::SPRING:
            if (weatherHash != MISC::GET_HASH_KEY("RAIN") &&
                weatherHash != MISC::GET_HASH_KEY("CLEARING")) {
                weatherCompatible = false;
            }
            break;
    }
    
    if (!weatherCompatible && event.isActive) {
        // Adapter l'événement
        for (auto& ritual : event.seasonalRituals) {
            // Déplacer les rituels à l'intérieur
            Vector3 indoorLocation;
            if (PATHFIND::GET_SAFE_COORD_FOR_PED(
                event.location.x, event.location.y, event.location.z,
                true, &indoorLocation, 16
            )) {
                ritual.location = indoorLocation;
            }
            
            // Ajuster la durée
            ritual.duration *= 0.8f;
        }
    }
}

void SeasonalEvents::handleSeasonChange() {
    // Créer un souvenir collectif du changement de saison
    CollectiveMemoryEvent seasonEvent;
    seasonEvent.type = MemoryType::POSITIVE;
    seasonEvent.importance = 0.7f;
    seasonEvent.description = "season_change_" + std::to_string(static_cast<int>(currentSeason));
    
    // Notifier tous les groupes
    for (const auto& [groupId, family] : FamilyRelations::getInstance().getAllFamilies()) {
        CollectiveMemory::getInstance().recordEvent(groupId, seasonEvent);
        
        // Adapter les comportements selon la saison
        switch (currentSeason) {
            case Season::WINTER:
                // Rassembler les ressources
                for (auto& member : family.members) {
                    if (ENTITY::DOES_ENTITY_EXIST(member.ped)) {
                        AI::TASK_GUARD_CURRENT_POSITION(
                            member.ped,
                            10.0f, 10.0f, true
                        );
                    }
                }
                break;
                
            case Season::SPRING:
                // Exploration et expansion
                for (auto& member : family.members) {
                    if (ENTITY::DOES_ENTITY_EXIST(member.ped)) {
                        AI::TASK_WANDER_IN_AREA(
                            member.ped,
                            family.homeLocation.x,
                            family.homeLocation.y,
                            family.homeLocation.z,
                            100.0f, 0, 0
                        );
                    }
                }
                break;
        }
    }
    
    // Planifier les événements saisonniers
    switch (currentSeason) {
        case Season::AUTUMN:
            initializeSeasonalEvent(SeasonalEventType::HARVEST_FESTIVAL);
            break;
            
        case Season::WINTER:
            initializeSeasonalEvent(SeasonalEventType::WINTER_SOLSTICE);
            break;
    }
}

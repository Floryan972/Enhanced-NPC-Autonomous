#include "trade_system.h"
#include "natives.h"
#include "seasonal_events.h"
#include "family_relations.h"
#include "alliance_system.h"
#include "reputation_system.h"

void TradeSystem::initializeTradeSystem() {
    // Créer des ressources de base pour chaque groupe
    for (const auto& [groupId, family] : FamilyRelations::getInstance().getAllFamilies()) {
        std::vector<Resource> baseResources;
        
        // Ressources alimentaires
        Resource food;
        food.type = ResourceType::FOOD;
        food.name = "basic_food";
        food.value = 1.0f;
        food.quantity = 100.0f;
        food.quality = 0.7f;
        food.origin = groupId;
        baseResources.push_back(food);
        
        // Matériaux
        Resource materials;
        materials.type = ResourceType::MATERIALS;
        materials.name = "basic_materials";
        materials.value = 1.5f;
        materials.quantity = 50.0f;
        materials.quality = 0.6f;
        materials.origin = groupId;
        baseResources.push_back(materials);
        
        groupResources[groupId] = baseResources;
    }
    
    // Créer des marchés initiaux
    for (const auto& [groupId, family] : FamilyRelations::getInstance().getAllFamilies()) {
        if (family.familyHonor > 0.7f) {
            createMarketplace(family.homeLocation);
        }
    }
}

void TradeSystem::establishTradeRoute(const std::string& startGroup, const std::string& endGroup) {
    std::string routeId = startGroup + "_" + endGroup + "_" + std::to_string(MISC::GET_GAME_TIMER());
    
    TradeRoute route;
    route.routeId = routeId;
    route.isActive = true;
    route.controllingGroups = {startGroup, endGroup};
    
    // Créer des points de passage
    auto& startFamily = FamilyRelations::getInstance().getFamily(startGroup);
    auto& endFamily = FamilyRelations::getInstance().getFamily(endGroup);
    
    Vector3 startPos = startFamily.homeLocation;
    Vector3 endPos = endFamily.homeLocation;
    
    // Générer des points intermédiaires
    int numWaypoints = 3;
    for (int i = 0; i <= numWaypoints; i++) {
        float t = static_cast<float>(i) / numWaypoints;
        Vector3 waypoint = {
            startPos.x + (endPos.x - startPos.x) * t,
            startPos.y + (endPos.y - startPos.y) * t,
            0.0f
        };
        
        // Trouver une hauteur de terrain valide
        if (MISC::GET_GROUND_Z_FOR_3D_COORD(
            waypoint.x, waypoint.y, 1000.0f,
            &waypoint.z, false
        )) {
            route.waypoints.push_back(waypoint);
        }
    }
    
    // Calculer le risque et la distance
    route.risk = calculateRouteRisk(route);
    route.distance = SYSTEM::VDIST(
        startPos.x, startPos.y, startPos.z,
        endPos.x, endPos.y, endPos.z
    );
    
    tradeRoutes[routeId] = route;
}

float TradeSystem::calculateRouteRisk(const TradeRoute& route) {
    float risk = 0.0f;
    
    // Facteurs de risque
    for (size_t i = 0; i < route.waypoints.size() - 1; i++) {
        const auto& current = route.waypoints[i];
        const auto& next = route.waypoints[i + 1];
        
        // Vérifier la présence d'ennemis
        const int MAX_NEARBY_PEDS = 30;
        Ped nearbyPeds[MAX_NEARBY_PEDS];
        int count = worldGetAllPeds(nearbyPeds, MAX_NEARBY_PEDS);
        
        for (int j = 0; j < count; j++) {
            Ped ped = nearbyPeds[j];
            if (!ENTITY::DOES_ENTITY_EXIST(ped)) continue;
            
            // Vérifier si le PED est hostile
            auto* reputation = ReputationSystem::getInstance().getReputation(ped);
            if (reputation && reputation->type == ReputationType::HOSTILE) {
                risk += 0.1f;
            }
        }
        
        // Vérifier le terrain
        float groundZ;
        if (MISC::GET_GROUND_Z_FOR_3D_COORD(
            current.x, current.y, current.z,
            &groundZ, false
        )) {
            float heightDiff = abs(groundZ - current.z);
            risk += heightDiff / 100.0f; // Terrain accidenté augmente le risque
        }
    }
    
    // Facteurs saisonniers
    auto& seasonalSystem = SeasonalEvents::getInstance();
    if (seasonalSystem.getCurrentSeason() == Season::WINTER) {
        risk *= 1.5f; // Plus risqué en hiver
    }
    
    return std::clamp(risk, 0.0f, 1.0f);
}

void TradeSystem::updateTrade() {
    // Mettre à jour les routes commerciales
    updateTradeRoutes();
    
    // Mettre à jour les prix des ressources
    updateResourcePrices();
    
    // Gérer les accords commerciaux actifs
    for (auto& [agreementId, agreement] : activeAgreements) {
        if (agreement.status != TradeStatus::ACTIVE) continue;
        
        // Vérifier si l'accord est terminé
        if (MISC::GET_GAME_TIMER() > agreement.duration) {
            executeTradeAgreement(agreementId);
        }
        
        // Vérifier les conditions de route
        float currentRisk = calculateRouteRisk(agreement.route);
        if (currentRisk > 0.8f) {
            // Route trop dangereuse, suspendre le commerce
            agreement.status = TradeStatus::FAILED;
            handleTradeDispute(agreementId);
        }
    }
    
    // Mettre à jour la demande du marché
    updateMarketDemand();
}

void TradeSystem::updateResourcePrices() {
    // Facteurs affectant les prix
    Season currentSeason = SeasonalEvents::getInstance().getCurrentSeason();
    
    for (auto& [groupId, resources] : groupResources) {
        for (auto& resource : resources) {
            float priceModifier = 1.0f;
            
            // Modification saisonnière
            switch (resource.type) {
                case ResourceType::FOOD:
                    if (currentSeason == Season::WINTER) {
                        priceModifier *= 1.5f; // Nourriture plus chère en hiver
                    } else if (currentSeason == Season::AUTUMN) {
                        priceModifier *= 0.8f; // Moins chère après la récolte
                    }
                    break;
                    
                case ResourceType::MATERIALS:
                    if (currentSeason == Season::SPRING) {
                        priceModifier *= 0.9f; // Matériaux plus disponibles
                    }
                    break;
            }
            
            // Rareté
            if (resource.quantity < 20.0f) {
                priceModifier *= 1.5f;
                resource.isRare = true;
            } else {
                resource.isRare = false;
            }
            
            // Qualité
            priceModifier *= (0.5f + resource.quality);
            
            // Mettre à jour la valeur
            resource.value *= priceModifier;
        }
    }
}

void TradeSystem::createMarketplace(const Vector3& location) {
    // Vérifier si un marché existe déjà à proximité
    for (const auto& existing : marketplaces) {
        float distance = SYSTEM::VDIST(
            location.x, location.y, location.z,
            existing.x, existing.y, existing.z
        );
        
        if (distance < 100.0f) return; // Trop proche d'un marché existant
    }
    
    // Trouver un bon emplacement
    Vector3 marketLocation;
    if (PATHFIND::GET_SAFE_COORD_FOR_PED(
        location.x, location.y, location.z,
        true, &marketLocation, 16
    )) {
        marketplaces.push_back(marketLocation);
        
        // Créer des PNJ marchands
        const int NUM_MERCHANTS = 5;
        for (int i = 0; i < NUM_MERCHANTS; i++) {
            // Logique de création de PNJ marchands
            float angle = (2.0f * 3.14159f * i) / NUM_MERCHANTS;
            Vector3 position = {
                marketLocation.x + 5.0f * cos(angle),
                marketLocation.y + 5.0f * sin(angle),
                marketLocation.z
            };
            
            // Créer le PNJ
            // Note: La création spécifique dépend de l'API du jeu
        }
    }
}

void TradeSystem::handleSeasonalTrade() {
    Season currentSeason = SeasonalEvents::getInstance().getCurrentSeason();
    
    // Ajuster les ressources selon la saison
    for (auto& [groupId, resources] : groupResources) {
        switch (currentSeason) {
            case Season::AUTUMN:
                // Augmenter les ressources alimentaires après la récolte
                for (auto& resource : resources) {
                    if (resource.type == ResourceType::FOOD) {
                        resource.quantity *= 1.5f;
                    }
                }
                break;
                
            case Season::WINTER:
                // Diminuer les ressources et augmenter la demande
                for (auto& resource : resources) {
                    resource.quantity *= 0.8f;
                    if (resource.type == ResourceType::FOOD ||
                        resource.type == ResourceType::MEDICINE) {
                        resource.value *= 1.3f;
                    }
                }
                break;
                
            case Season::SPRING:
                // Nouvelles ressources disponibles
                Resource herbs;
                herbs.type = ResourceType::MEDICINE;
                herbs.name = "spring_herbs";
                herbs.value = 2.0f;
                herbs.quantity = 30.0f;
                herbs.quality = 0.9f;
                herbs.origin = groupId;
                resources.push_back(herbs);
                break;
        }
    }
    
    // Mettre à jour les routes commerciales
    for (auto& [routeId, route] : tradeRoutes) {
        route.risk = calculateRouteRisk(route);
        
        // Fermer les routes trop dangereuses en hiver
        if (currentSeason == Season::WINTER && route.risk > 0.7f) {
            route.isActive = false;
        } else {
            route.isActive = true;
        }
    }
}

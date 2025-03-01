#pragma once
#include "types.h"
#include <unordered_map>
#include <vector>
#include <string>

enum class ResourceType {
    FOOD,
    MATERIALS,
    WEAPONS,
    TOOLS,
    LUXURIES,
    MEDICINE
};

enum class TradeStatus {
    PROPOSED,
    NEGOTIATING,
    ACTIVE,
    COMPLETED,
    FAILED
};

struct Resource {
    ResourceType type;
    std::string name;
    float value;
    float quantity;
    bool isRare;
    std::string origin;
    float quality;
};

struct TradeRoute {
    std::string routeId;
    std::vector<Vector3> waypoints;
    float risk;
    float distance;
    bool isActive;
    std::vector<std::string> controllingGroups;
};

struct TradeAgreement {
    std::string agreementId;
    std::string seller;
    std::string buyer;
    std::vector<Resource> resources;
    float totalValue;
    TradeStatus status;
    TradeRoute route;
    float duration;
};

class TradeSystem {
public:
    static TradeSystem& getInstance() {
        static TradeSystem instance;
        return instance;
    }

    void initializeTradeSystem();
    void updateTrade();
    void proposeTradeAgreement(const std::string& seller, const std::string& buyer, const std::vector<Resource>& resources);
    void executeTradeAgreement(const std::string& agreementId);
    
    // Nouvelles fonctions commerciales
    void establishTradeRoute(const std::string& startGroup, const std::string& endGroup);
    void updatePrices(const std::string& marketId);
    void handleTradeDispute(const std::string& agreementId);
    float calculateResourceValue(const Resource& resource);
    
    // Gestion des marchés
    void createMarketplace(const Vector3& location);
    void updateMarketDemand();
    void handleSeasonalTrade();

private:
    TradeSystem() {}
    std::unordered_map<std::string, TradeAgreement> activeAgreements;
    std::unordered_map<std::string, std::vector<Resource>> groupResources;
    std::unordered_map<std::string, TradeRoute> tradeRoutes;
    std::vector<Vector3> marketplaces;
    
    void updateTradeRoutes();
    void distributeResources(const TradeAgreement& agreement);
    float calculateRouteRisk(const TradeRoute& route);
    void updateResourcePrices();
};

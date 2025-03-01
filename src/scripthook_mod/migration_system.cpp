#include "migration_system.h"
#include "natives.h"
#include "seasonal_events.h"
#include "trade_system.h"
#include "family_relations.h"
#include "alliance_system.h"

void MigrationSystem::initializeMigrationSystem() {
    // Créer des colonies initiales
    for (const auto& [groupId, family] : FamilyRelations::getInstance().getAllFamilies()) {
        TerrainType terrain = TerrainType::PLAINS; // Par défaut
        
        // Déterminer le type de terrain
        Vector3 location = family.homeLocation;
        float groundZ;
        if (MISC::GET_GROUND_Z_FOR_3D_COORD(
            location.x, location.y, 1000.0f,
            &groundZ, false
        )) {
            float height = groundZ;
            if (height > 100.0f) {
                terrain = TerrainType::MOUNTAIN;
            } else if (WATER::TEST_VERTICAL_PROBE_AGAINST_ALL_WATER(
                location.x, location.y, location.z,
                0, nullptr
            )) {
                terrain = TerrainType::COASTAL;
            }
        }
        
        createSettlement(location, terrain);
    }
}

void MigrationSystem::createSettlement(const Vector3& location, TerrainType terrain) {
    std::string settlementId = "settlement_" + std::to_string(MISC::GET_GAME_TIMER());
    
    Settlement settlement;
    settlement.settlementId = settlementId;
    settlement.location = location;
    settlement.terrain = terrain;
    
    // Configurer selon le terrain
    switch (terrain) {
        case TerrainType::MOUNTAIN:
            settlement.capacity = 50.0f;
            settlement.resources = 70.0f;
            settlement.isSeasonal = true; // Migrations saisonnières en montagne
            break;
            
        case TerrainType::COASTAL:
            settlement.capacity = 100.0f;
            settlement.resources = 90.0f;
            settlement.isSeasonal = false;
            break;
            
        case TerrainType::PLAINS:
            settlement.capacity = 150.0f;
            settlement.resources = 100.0f;
            settlement.isSeasonal = false;
            break;
    }
    
    settlements[settlementId] = settlement;
}

void MigrationSystem::planMigration(const std::string& groupId, MigrationType type) {
    std::string planId = groupId + "_migration_" + std::to_string(MISC::GET_GAME_TIMER());
    
    MigrationPlan plan;
    plan.planId = planId;
    plan.groupId = groupId;
    plan.type = type;
    plan.isActive = false;
    plan.progress = 0.0f;
    
    // Trouver l'origine
    auto& family = FamilyRelations::getInstance().getFamily(groupId);
    for (const auto& [id, settlement] : settlements) {
        float distance = SYSTEM::VDIST(
            settlement.location.x, settlement.location.y, settlement.location.z,
            family.homeLocation.x, family.homeLocation.y, family.homeLocation.z
        );
        
        if (distance < 10.0f) {
            plan.origin = &settlements[id];
            break;
        }
    }
    
    // Trouver la destination selon le type
    switch (type) {
        case MigrationType::SEASONAL:
        {
            Season currentSeason = SeasonalEvents::getInstance().getCurrentSeason();
            TerrainType preferredTerrain;
            
            if (currentSeason == Season::WINTER) {
                preferredTerrain = TerrainType::PLAINS; // Descendre des montagnes
            } else if (currentSeason == Season::SUMMER) {
                preferredTerrain = TerrainType::MOUNTAIN; // Monter en altitude
            }
            
            // Trouver la meilleure destination
            float bestScore = -1.0f;
            for (auto& [id, settlement] : settlements) {
                if (settlement.terrain == preferredTerrain &&
                    settlement.capacity > settlement.residentGroups.size()) {
                    float score = settlement.resources;
                    
                    if (score > bestScore) {
                        bestScore = score;
                        plan.destination = &settlement;
                    }
                }
            }
            break;
        }
        
        case MigrationType::RESOURCE_DRIVEN:
        {
            // Trouver la colonie avec le plus de ressources
            float maxResources = -1.0f;
            for (auto& [id, settlement] : settlements) {
                if (settlement.resources > maxResources &&
                    settlement.capacity > settlement.residentGroups.size()) {
                    maxResources = settlement.resources;
                    plan.destination = &settlement;
                }
            }
            break;
        }
    }
    
    if (plan.origin && plan.destination) {
        // Créer un chemin de migration
        MigrationPath path;
        path.pathId = planId + "_path";
        
        // Générer des points de passage
        Vector3 startPos = plan.origin->location;
        Vector3 endPos = plan.destination->location;
        
        int numWaypoints = 5;
        for (int i = 0; i <= numWaypoints; i++) {
            float t = static_cast<float>(i) / numWaypoints;
            Vector3 waypoint = {
                startPos.x + (endPos.x - startPos.x) * t,
                startPos.y + (endPos.y - startPos.y) * t,
                0.0f
            };
            
            if (MISC::GET_GROUND_Z_FOR_3D_COORD(
                waypoint.x, waypoint.y, 1000.0f,
                &waypoint.z, false
            )) {
                path.waypoints.push_back(waypoint);
            }
        }
        
        path.terrain = plan.origin->terrain;
        path.difficulty = calculatePathDifficulty(path);
        path.distance = SYSTEM::VDIST(
            startPos.x, startPos.y, startPos.z,
            endPos.x, endPos.y, endPos.z
        );
        path.isActive = true;
        
        plan.path = path;
        activePlans[planId] = plan;
    }
}

float MigrationSystem::calculatePathDifficulty(const MigrationPath& path) {
    float difficulty = 0.0f;
    
    // Facteurs de difficulté
    for (size_t i = 0; i < path.waypoints.size() - 1; i++) {
        const auto& current = path.waypoints[i];
        const auto& next = path.waypoints[i + 1];
        
        // Différence de hauteur
        float heightDiff = abs(next.z - current.z);
        difficulty += heightDiff / 100.0f;
        
        // Vérifier le terrain
        if (path.terrain == TerrainType::MOUNTAIN) {
            difficulty *= 1.5f;
        } else if (path.terrain == TerrainType::DESERT) {
            difficulty *= 1.3f;
        }
        
        // Vérifier les obstacles
        const int MAX_OBJECTS = 10;
        Object nearbyObjects[MAX_OBJECTS];
        int count = worldGetAllObjects(nearbyObjects, MAX_OBJECTS);
        
        for (int j = 0; j < count; j++) {
            Object obj = nearbyObjects[j];
            if (!ENTITY::DOES_ENTITY_EXIST(obj)) continue;
            
            Vector3 objPos = ENTITY::GET_ENTITY_COORDS(obj, true);
            float distance = SYSTEM::VDIST(
                current.x, current.y, current.z,
                objPos.x, objPos.y, objPos.z
            );
            
            if (distance < 5.0f) {
                difficulty += 0.1f;
            }
        }
    }
    
    // Facteurs saisonniers
    Season currentSeason = SeasonalEvents::getInstance().getCurrentSeason();
    if (currentSeason == Season::WINTER) {
        difficulty *= 2.0f;
    } else if (currentSeason == Season::SPRING) {
        difficulty *= 1.2f; // Pluies
    }
    
    return std::clamp(difficulty, 0.0f, 1.0f);
}

void MigrationSystem::handleSeasonalMigration() {
    Season currentSeason = SeasonalEvents::getInstance().getCurrentSeason();
    
    // Vérifier chaque colonie saisonnière
    for (auto& [settlementId, settlement] : settlements) {
        if (!settlement.isSeasonal) continue;
        
        bool shouldEvacuate = false;
        
        // Conditions d'évacuation
        if (settlement.terrain == TerrainType::MOUNTAIN && 
            currentSeason == Season::WINTER) {
            shouldEvacuate = true;
        }
        
        if (shouldEvacuate) {
            // Évacuer les groupes
            for (const auto& groupId : settlement.residentGroups) {
                planMigration(groupId, MigrationType::SEASONAL);
            }
            
            // Réduire les ressources
            settlement.resources *= 0.5f;
        }
    }
    
    // Mettre à jour les chemins de migration
    for (auto& [pathId, path] : knownPaths) {
        path.difficulty = calculatePathDifficulty(path);
        
        // Fermer les chemins dangereux
        if (path.difficulty > 0.8f) {
            path.isActive = false;
        }
    }
}

void MigrationSystem::updateMigration() {
    // Mettre à jour les migrations actives
    for (auto& [planId, plan] : activePlans) {
        if (!plan.isActive) continue;
        
        // Mettre à jour la progression
        float progressDelta = 0.01f / plan.path.difficulty;
        plan.progress = std::min(plan.progress + progressDelta, 1.0f);
        
        // Déplacer les membres du groupe
        for (const auto& memberId : plan.participatingMembers) {
            Ped member = std::stoi(memberId);
            if (!ENTITY::DOES_ENTITY_EXIST(member)) continue;
            
            // Calculer la position actuelle sur le chemin
            size_t currentWaypointIndex = static_cast<size_t>(
                plan.progress * (plan.path.waypoints.size() - 1)
            );
            
            if (currentWaypointIndex < plan.path.waypoints.size()) {
                const auto& targetPos = plan.path.waypoints[currentWaypointIndex];
                
                AI::TASK_GO_TO_COORD_ANY_MEANS(
                    member,
                    targetPos.x, targetPos.y, targetPos.z,
                    2.0f, 0, 0, 786603, 0xbf800000
                );
            }
        }
        
        // Vérifier si la migration est terminée
        if (plan.progress >= 1.0f) {
            // Mettre à jour les colonies
            plan.origin->residentGroups.erase(
                std::remove(plan.origin->residentGroups.begin(),
                          plan.origin->residentGroups.end(),
                          plan.groupId),
                plan.origin->residentGroups.end()
            );
            
            plan.destination->residentGroups.push_back(plan.groupId);
            
            // Mettre à jour la position du groupe
            auto& family = FamilyRelations::getInstance().getFamily(plan.groupId);
            family.homeLocation = plan.destination->location;
            
            // Créer un souvenir de la migration
            CollectiveMemoryEvent migrationMemory;
            migrationMemory.type = MemoryType::POSITIVE;
            migrationMemory.importance = 0.8f;
            migrationMemory.description = "group_migration";
            migrationMemory.location = plan.destination->location;
            
            CollectiveMemory::getInstance().recordEvent(plan.groupId, migrationMemory);
            
            plan.isActive = false;
        }
    }
    
    // Mettre à jour les conditions des colonies
    evaluateSettlementConditions();
    
    // Gérer les migrations saisonnières
    handleSeasonalMigration();
}

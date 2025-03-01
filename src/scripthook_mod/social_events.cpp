#include "social_events.h"
#include "natives.h"
#include "alliance_system.h"
#include "family_relations.h"
#include "group_rituals.h"
#include "collective_memory.h"

void SocialEvents::initializeEvent(SocialEventType type, const std::vector<std::string>& groups) {
    std::string eventId = "event_" + std::to_string(MISC::GET_GAME_TIMER());
    
    SocialEvent event;
    event.type = type;
    event.eventId = eventId;
    event.participatingGroups = groups;
    event.isActive = false;
    
    // Configurer les exigences selon le type
    switch (type) {
        case SocialEventType::WEDDING:
            event.requirements.requiredRoles = {"PRIEST", "WITNESSES"};
            event.requirements.minimumHonor = 0.6f;
            event.requirements.minimumParticipants = 10;
            event.duration = 1800.0f; // 30 minutes
            event.importance = 1.0f;
            break;
            
        case SocialEventType::CORONATION:
            event.requirements.requiredRoles = {"ELDER", "GUARDS"};
            event.requirements.minimumHonor = 0.8f;
            event.requirements.minimumParticipants = 20;
            event.duration = 3600.0f; // 1 heure
            event.importance = 1.0f;
            break;
            
        case SocialEventType::TOURNAMENT:
            event.requirements.requiredRoles = {"CHAMPIONS", "JUDGES"};
            event.requirements.minimumHonor = 0.5f;
            event.requirements.minimumParticipants = 15;
            event.duration = 7200.0f; // 2 heures
            event.importance = 0.8f;
            break;
    }
    
    // Configurer l'emplacement
    setupEventLocation(event);
    
    // Créer les rituels associés
    createEventRituals(event);
    
    activeEvents[eventId] = event;
    
    // Mettre à jour les références des groupes
    for (const auto& groupId : groups) {
        groupEvents[groupId].push_back(eventId);
    }
}

void SocialEvents::setupEventLocation(SocialEvent& event) {
    // Trouver le meilleur emplacement selon le type d'événement
    Vector3 bestLocation;
    float bestScore = -1.0f;
    
    // Vérifier les emplacements significatifs de chaque groupe
    for (const auto& groupId : event.participatingGroups) {
        auto& family = FamilyRelations::getInstance().getFamily(groupId);
        
        // Évaluer l'emplacement de la famille
        float score = 0.0f;
        
        // Vérifier l'accessibilité
        bool isAccessible = PATHFIND::GET_SAFE_COORD_FOR_PED(
            family.homeLocation.x, family.homeLocation.y, family.homeLocation.z,
            true, &bestLocation, 16
        );
        
        if (isAccessible) {
            score += 0.5f;
            
            // Vérifier l'espace disponible
            const int MAX_NEARBY_PEDS = 30;
            Ped nearbyPeds[MAX_NEARBY_PEDS];
            int count = worldGetAllPeds(nearbyPeds, MAX_NEARBY_PEDS);
            
            if (count < event.requirements.minimumParticipants) {
                score += 0.3f;
            }
            
            // Vérifier la sécurité
            if (!MISC::IS_PROJECTILE_IN_AREA(
                bestLocation.x - 50.0f, bestLocation.y - 50.0f, bestLocation.z - 50.0f,
                bestLocation.x + 50.0f, bestLocation.y + 50.0f, bestLocation.z + 50.0f,
                false
            )) {
                score += 0.2f;
            }
        }
        
        if (score > bestScore) {
            bestScore = score;
            event.location = bestLocation;
        }
    }
}

void SocialEvents::createEventRituals(SocialEvent& event) {
    switch (event.type) {
        case SocialEventType::WEDDING:
        {
            // Rituel de cérémonie
            Ritual ceremony;
            ceremony.type = RitualType::CEREMONY;
            ceremony.importance = 1.0f;
            ceremony.location = event.location;
            
            RitualPhase procession;
            procession.name = "wedding_procession";
            procession.duration = 300.0f;
            procession.animations = {"WORLD_HUMAN_GUARD_PATROL"};
            
            RitualPhase vows;
            vows.name = "wedding_vows";
            vows.duration = 180.0f;
            vows.animations = {"WORLD_HUMAN_GUARD_STAND"};
            
            ceremony.phases = {procession, vows};
            event.associatedRituals.push_back(ceremony);
            
            // Rituel de célébration
            Ritual celebration;
            celebration.type = RitualType::CELEBRATION;
            celebration.importance = 0.8f;
            celebration.location = event.location;
            
            RitualPhase feast;
            feast.name = "wedding_feast";
            feast.duration = 600.0f;
            feast.animations = {"WORLD_HUMAN_PARTYING"};
            
            celebration.phases = {feast};
            event.associatedRituals.push_back(celebration);
            break;
        }
        
        case SocialEventType::TOURNAMENT:
        {
            // Rituel d'ouverture
            Ritual opening;
            opening.type = RitualType::CEREMONY;
            opening.importance = 0.9f;
            
            RitualPhase parade;
            parade.name = "tournament_parade";
            parade.duration = 300.0f;
            parade.animations = {"WORLD_HUMAN_GUARD_PATROL"};
            
            opening.phases = {parade};
            event.associatedRituals.push_back(opening);
            
            // Rituels de combat
            Ritual combat;
            combat.type = RitualType::TRAINING;
            combat.importance = 0.8f;
            
            RitualPhase duel;
            duel.name = "tournament_duel";
            duel.duration = 180.0f;
            duel.animations = {"WORLD_HUMAN_GUARD_STAND"};
            
            combat.phases = {duel};
            event.associatedRituals.push_back(combat);
            break;
        }
    }
}

void SocialEvents::handleEventOutcome(const std::string& eventId) {
    auto& event = activeEvents[eventId];
    
    // Créer un souvenir collectif
    CollectiveMemoryEvent memoryEvent;
    memoryEvent.type = MemoryType::POSITIVE;
    memoryEvent.importance = event.importance;
    memoryEvent.location = event.location;
    memoryEvent.description = "social_event_" + std::to_string(static_cast<int>(event.type));
    
    // Mettre à jour les relations entre groupes
    for (const auto& groupId : event.participatingGroups) {
        // Enregistrer le souvenir
        CollectiveMemory::getInstance().recordEvent(groupId, memoryEvent);
        
        // Renforcer les liens
        auto& family = FamilyRelations::getInstance().getFamily(groupId);
        family.familyHonor = std::min(family.familyHonor + 0.1f, 1.0f);
        
        // Mettre à jour les alliances
        for (const auto& otherGroupId : event.participatingGroups) {
            if (groupId != otherGroupId) {
                AllianceSystem::getInstance().handleAllianceEvent(
                    groupId + "_" + otherGroupId,
                    "cooperation"
                );
            }
        }
    }
}

void SocialEvents::synchronizeWithTraditions(const std::string& eventId) {
    auto& event = activeEvents[eventId];
    
    // Collecter toutes les traditions pertinentes
    std::vector<std::string> relevantTraditions;
    for (const auto& groupId : event.participatingGroups) {
        auto& family = FamilyRelations::getInstance().getFamily(groupId);
        
        for (const auto& tradition : family.traditions) {
            if (std::find(relevantTraditions.begin(),
                         relevantTraditions.end(),
                         tradition) == relevantTraditions.end()) {
                relevantTraditions.push_back(tradition);
            }
        }
    }
    
    // Adapter les rituels selon les traditions
    for (auto& ritual : event.associatedRituals) {
        for (const auto& tradition : relevantTraditions) {
            // Ajouter des phases spécifiques aux traditions
            RitualPhase traditionalPhase;
            traditionalPhase.name = "traditional_" + tradition;
            traditionalPhase.duration = 180.0f;
            traditionalPhase.animations = {"WORLD_HUMAN_CHEERING"};
            
            ritual.phases.push_back(traditionalPhase);
        }
    }
}

bool SocialEvents::canGroupParticipate(const std::string& groupId, const std::string& eventId) {
    auto& event = activeEvents[eventId];
    auto& family = FamilyRelations::getInstance().getFamily(groupId);
    
    // Vérifier l'honneur
    if (family.familyHonor < event.requirements.minimumHonor) {
        return false;
    }
    
    // Vérifier le nombre de participants
    int availableMembers = 0;
    for (const auto& member : family.members) {
        if (ENTITY::DOES_ENTITY_EXIST(member.ped)) {
            availableMembers++;
        }
    }
    
    if (availableMembers < event.requirements.minimumParticipants) {
        return false;
    }
    
    // Vérifier les rôles requis
    for (const auto& role : event.requirements.requiredRoles) {
        bool hasRole = false;
        for (const auto& member : family.members) {
            auto* hierarchy = SocialHierarchy::getInstance().getMemberPosition(member.ped);
            if (hierarchy) {
                for (const auto& memberRole : hierarchy->roles) {
                    if (std::to_string(static_cast<int>(memberRole)) == role) {
                        hasRole = true;
                        break;
                    }
                }
            }
            if (hasRole) break;
        }
        if (!hasRole) return false;
    }
    
    return true;
}

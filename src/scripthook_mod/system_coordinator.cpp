#include "system_coordinator.h"
#include "natives.h"

void SystemCoordinator::update() {
    // Mettre à jour tous les systèmes dans un ordre spécifique
    EventManager::getInstance().updateEvents();
    CollectiveMemory::getInstance().updateMemories();
    SocialGroupSystem::getInstance().updateGroups();
    PersonalitySystem::getInstance().updateEmotionalStates();
    RoutineSystem::getInstance().updateRoutines();
    ReputationSystem::getInstance().updateSocialStatus();

    // Gérer les interactions entre systèmes
    updateGroupDynamics();
    updateEnvironmentalEffects();
    handleSystemConflicts();
    propagateSystemEffects();
    cleanupInvalidEntities();
}

void SystemCoordinator::handleWeatherChange(const std::string& weatherType) {
    Vector3 playerPos = ENTITY::GET_ENTITY_COORDS(PLAYER::PLAYER_PED_ID(), true);
    
    // Enregistrer l'événement météo
    CollectiveMemory::getInstance().recordWeatherEvent(playerPos, weatherType);
    
    // Déclencher des événements spéciaux basés sur la météo
    if (weatherType == "THUNDER") {
        EventManager::getInstance().triggerEvent(
            SpecialEventType::EMERGENCY,
            playerPos,
            200.0f
        );
    }

    // Mettre à jour les routines
    const int MAX_PEDS = 30;
    Ped peds[MAX_PEDS];
    int count = worldGetAllPeds(peds, MAX_PEDS);

    for (int i = 0; i < count; i++) {
        Ped ped = peds[i];
        if (!ENTITY::DOES_ENTITY_EXIST(ped)) continue;

        // Interrompre ou modifier les routines selon la météo
        if (weatherType == "RAIN" || weatherType == "THUNDER") {
            RoutineSystem::getInstance().interruptRoutine(ped);
        } else {
            RoutineSystem::getInstance().resumeRoutine(ped);
        }
    }
}

void SystemCoordinator::handleCombatEvent(Ped attacker, Ped victim) {
    // Créer un événement de mémoire collective
    CollectiveMemoryEvent combatEvent;
    combatEvent.type = MemoryType::THREAT;
    combatEvent.location = ENTITY::GET_ENTITY_COORDS(attacker, true);
    combatEvent.importance = 0.8f;
    combatEvent.timeStamp = MISC::GET_GAME_TIMER() / 1000.0f;
    combatEvent.mainActor = attacker;
    combatEvent.involvedPeds = {attacker, victim};

    // Propager l'événement aux groupes proches
    for (auto& [groupId, _] : SocialGroupSystem::getInstance().getGroups()) {
        CollectiveMemory::getInstance().recordEvent(groupId, combatEvent);
    }

    // Mettre à jour les réputations
    ReputationSystem::getInstance().recordCrime(attacker, 0.5f);
    
    // Déclencher des réactions de groupe
    Vector3 combatPos = ENTITY::GET_ENTITY_COORDS(attacker, true);
    EventManager::getInstance().triggerEvent(
        SpecialEventType::GANG_WAR,
        combatPos,
        50.0f
    );
}

void SystemCoordinator::updateGroupDynamics() {
    // Mettre à jour les relations entre groupes
    for (auto& [groupId, group] : SocialGroupSystem::getInstance().getGroups()) {
        float groupTension = CollectiveMemory::getInstance().getGroupMemory(groupId).groupTension;
        
        // Ajuster les comportements de groupe basés sur la tension
        if (groupTension > 0.7f) {
            // Augmenter la cohésion du groupe
            group.groupCohesion = std::min(group.groupCohesion + 0.1f, 1.0f);
            
            // Mettre à jour les formations
            SocialGroupSystem::getInstance().handleGroupFormation(group);
        }

        // Mettre à jour les réputations de groupe
        for (auto& member : group.members) {
            ReputationSystem::getInstance().updateReputation(
                member.pedHandle,
                group.groupCohesion * 0.1f
            );
        }
    }
}

void SystemCoordinator::updateEnvironmentalEffects() {
    // Obtenir la météo actuelle
    Hash weather = MISC::GET_PREV_WEATHER_TYPE_HASH_NAME();
    
    // Mettre à jour les comportements environnementaux
    const int MAX_PEDS = 30;
    Ped peds[MAX_PEDS];
    int count = worldGetAllPeds(peds, MAX_PEDS);

    for (int i = 0; i < count; i++) {
        Ped ped = peds[i];
        if (!ENTITY::DOES_ENTITY_EXIST(ped)) continue;

        Vector3 pedPos = ENTITY::GET_ENTITY_COORDS(ped, true);
        
        // Vérifier les événements actifs dans la zone
        for (const auto& event : EventManager::getInstance().getActiveEvents()) {
            if (event.isActive) {
                float distance = SYSTEM::VDIST(
                    pedPos.x, pedPos.y, pedPos.z,
                    event.epicenter.x, event.epicenter.y, event.epicenter.z
                );

                if (distance < event.radius) {
                    // Adapter le comportement selon l'événement et la personnalité
                    auto* personality = PersonalitySystem::getInstance().getPersonality(ped);
                    if (personality) {
                        EventManager::getInstance().updateNPCBehavior(ped, event);
                    }
                }
            }
        }
    }
}

void SystemCoordinator::handleSystemConflicts() {
    // Gérer les conflits entre différents systèmes
    const int MAX_PEDS = 30;
    Ped peds[MAX_PEDS];
    int count = worldGetAllPeds(peds, MAX_PEDS);

    for (int i = 0; i < count; i++) {
        Ped ped = peds[i];
        if (!ENTITY::DOES_ENTITY_EXIST(ped)) continue;

        // Vérifier les conflits entre routine et événements
        if (EventManager::getInstance().hasActiveEventNear(ENTITY::GET_ENTITY_COORDS(ped, true))) {
            RoutineSystem::getInstance().interruptRoutine(ped);
        }

        // Vérifier les conflits entre personnalité et groupe
        auto* personality = PersonalitySystem::getInstance().getPersonality(ped);
        if (personality && personality->type == PersonalityType::AGGRESSIVE) {
            // Empêcher les comportements agressifs dans les zones sûres
            if (SocialGroupSystem::getInstance().isInSafeZone(ped)) {
                personality->aggression = std::min(personality->aggression, 0.3f);
            }
        }
    }
}

void SystemCoordinator::propagateSystemEffects() {
    // Propager les effets entre les systèmes
    const int MAX_PEDS = 30;
    Ped peds[MAX_PEDS];
    int count = worldGetAllPeds(peds, MAX_PEDS);

    for (int i = 0; i < count; i++) {
        Ped ped = peds[i];
        if (!ENTITY::DOES_ENTITY_EXIST(ped)) continue;

        // Propager la réputation aux membres du groupe
        auto* reputation = ReputationSystem::getInstance().getReputation(ped);
        if (reputation) {
            ReputationSystem::getInstance().propagateReputation(ped, 20.0f);
        }

        // Mettre à jour la mémoire collective basée sur les événements
        Vector3 pedPos = ENTITY::GET_ENTITY_COORDS(ped, true);
        auto relevantMemories = CollectiveMemory::getInstance().getRelevantMemories(
            SocialGroupSystem::getInstance().getGroupId(ped),
            pedPos
        );

        // Adapter le comportement basé sur les souvenirs
        for (const auto& memory : relevantMemories) {
            if (memory.type == MemoryType::THREAT) {
                // Augmenter la vigilance
                PED::SET_PED_ALERTNESS(ped, 3);
            }
        }
    }
}

void SystemCoordinator::cleanupInvalidEntities() {
    // Nettoyer les entités invalides de tous les systèmes
    const int MAX_PEDS = 30;
    Ped peds[MAX_PEDS];
    int count = worldGetAllPeds(peds, MAX_PEDS);

    std::vector<Ped> invalidPeds;
    for (int i = 0; i < count; i++) {
        Ped ped = peds[i];
        if (!ENTITY::DOES_ENTITY_EXIST(ped)) {
            invalidPeds.push_back(ped);
        }
    }

    // Nettoyer les peds invalides de tous les systèmes
    for (Ped ped : invalidPeds) {
        ReputationSystem::getInstance().removeEntity(ped);
        SocialGroupSystem::getInstance().removeFromAllGroups(ped);
        RoutineSystem::getInstance().removeRoutine(ped);
        PersonalitySystem::getInstance().removePersonality(ped);
    }
}

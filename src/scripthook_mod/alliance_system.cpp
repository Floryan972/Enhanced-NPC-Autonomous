#include "alliance_system.h"
#include "natives.h"
#include "family_relations.h"
#include "group_rituals.h"
#include "collective_memory.h"
#include "social_hierarchy.h"

void AllianceSystem::initializeAlliance(const std::string& family1, const std::string& family2, AllianceType type) {
    std::string allianceId = family1 + "_" + family2 + "_" + std::to_string(MISC::GET_GAME_TIMER());
    
    Alliance alliance;
    alliance.allianceId = allianceId;
    alliance.type = type;
    alliance.status = AllianceStatus::PROPOSED;
    alliance.memberFamilies = {family1, family2};
    alliance.strength = 0.5f;
    alliance.trust = 0.5f;
    
    // Définir les termes de base
    AllianceTerms terms;
    terms.duration = 3600.0f; // 1 heure
    terms.penalty = 0.2f;
    
    switch (type) {
        case AllianceType::MARRIAGE:
            terms.obligations = {"protect_family", "share_resources", "attend_ceremonies"};
            terms.benefits = {"shared_territory", "mutual_aid", "combined_strength"};
            alliance.strength = 0.8f;
            break;
            
        case AllianceType::TRADE:
            terms.obligations = {"fair_trade", "protect_merchants"};
            terms.benefits = {"shared_resources", "economic_growth"};
            break;
            
        case AllianceType::MILITARY:
            terms.obligations = {"defend_allies", "share_intel", "joint_training"};
            terms.benefits = {"increased_security", "shared_territory"};
            break;
    }
    
    alliance.terms = terms;
    alliances[allianceId] = alliance;
    
    // Mettre à jour les références des familles
    familyAlliances[family1].push_back(allianceId);
    familyAlliances[family2].push_back(allianceId);
    
    // Créer un événement mémorable
    CollectiveMemoryEvent allianceEvent;
    allianceEvent.type = MemoryType::POSITIVE;
    allianceEvent.importance = 0.9f;
    allianceEvent.description = "alliance_formation";
    
    CollectiveMemory::getInstance().recordEvent(family1, allianceEvent);
    CollectiveMemory::getInstance().recordEvent(family2, allianceEvent);
}

void AllianceSystem::arrangeMarriage(const std::string& family1, const std::string& family2) {
    // Trouver des candidats éligibles
    auto& fam1 = FamilyRelations::getInstance().getFamily(family1);
    auto& fam2 = FamilyRelations::getInstance().getFamily(family2);
    
    Ped candidate1 = 0;
    Ped candidate2 = 0;
    
    // Sélectionner les meilleurs candidats
    for (const auto& member1 : fam1.members) {
        for (const auto& member2 : fam2.members) {
            auto* pers1 = PersonalitySystem::getInstance().getPersonality(member1.ped);
            auto* pers2 = PersonalitySystem::getInstance().getPersonality(member2.ped);
            
            if (pers1 && pers2 && 
                pers1->compatibility(*pers2) > 0.7f) {
                candidate1 = member1.ped;
                candidate2 = member2.ped;
                break;
            }
        }
        if (candidate1 != 0) break;
    }
    
    if (candidate1 != 0 && candidate2 != 0) {
        // Créer une alliance de mariage
        initializeAlliance(family1, family2, AllianceType::MARRIAGE);
        
        // Organiser la cérémonie
        Ritual weddingRitual;
        weddingRitual.type = RitualType::CEREMONY;
        weddingRitual.importance = 1.0f;
        weddingRitual.participants = {candidate1, candidate2};
        
        // Ajouter les membres des deux familles
        for (const auto& member : fam1.members) {
            weddingRitual.participants.push_back(member.ped);
        }
        for (const auto& member : fam2.members) {
            weddingRitual.participants.push_back(member.ped);
        }
        
        // Démarrer le rituel
        GroupRituals::getInstance().startRitual(family1, RitualType::CEREMONY);
        
        // Mettre à jour les relations familiales
        FamilyRelations::getInstance().updateFamilyTies(candidate1, candidate2, RelationType::SPOUSE);
    }
}

void AllianceSystem::updateAlliances() {
    for (auto& [allianceId, alliance] : alliances) {
        if (alliance.status != AllianceStatus::ACTIVE) continue;
        
        // Mettre à jour la force de l'alliance
        updateAllianceStrength(alliance);
        
        // Gérer les obligations
        handleObligations(alliance);
        
        // Distribuer les ressources
        distributeResources(alliance);
        
        // Résoudre les conflits
        resolveConflicts(alliance);
        
        // Vérifier les conditions de rupture
        if (alliance.strength < 0.2f || alliance.trust < 0.2f) {
            breakAlliance(allianceId, "alliance_deteriorated");
        }
    }
}

void AllianceSystem::updateAllianceStrength(Alliance& alliance) {
    float strengthDelta = 0.0f;
    
    // Vérifier le respect des obligations
    for (const auto& obligation : alliance.terms.obligations) {
        bool fulfilled = true; // Vérifier si l'obligation est remplie
        if (fulfilled) {
            strengthDelta += 0.01f;
            alliance.trust += 0.005f;
        } else {
            strengthDelta -= 0.02f;
            alliance.trust -= 0.01f;
        }
    }
    
    // Impact des interactions entre familles
    for (const auto& familyId : alliance.memberFamilies) {
        auto& family = FamilyRelations::getInstance().getFamily(familyId);
        strengthDelta += (family.familyHonor - 0.5f) * 0.01f;
    }
    
    // Mettre à jour la force
    alliance.strength = std::clamp(alliance.strength + strengthDelta, 0.0f, 1.0f);
    alliance.trust = std::clamp(alliance.trust, 0.0f, 1.0f);
}

void AllianceSystem::handleObligations(Alliance& alliance) {
    for (const auto& familyId : alliance.memberFamilies) {
        auto& family = FamilyRelations::getInstance().getFamily(familyId);
        
        // Vérifier chaque obligation
        for (const auto& obligation : alliance.terms.obligations) {
            if (obligation == "protect_family") {
                // Envoyer des protecteurs
                for (const auto& member : family.members) {
                    if (member.relation == RelationType::PARENT) {
                        // Assigner une tâche de protection
                        AI::TASK_GUARD_ASSIGNED_DEFENSIVE_AREA(
                            member.ped,
                            family.homeLocation.x, family.homeLocation.y, family.homeLocation.z,
                            10.0f, 10000.0f, 0
                        );
                    }
                }
            }
            else if (obligation == "share_resources") {
                // Partager les ressources
                distributeResources(alliance);
            }
        }
    }
}

void AllianceSystem::handleAllianceEvent(const std::string& allianceId, const std::string& eventType) {
    auto& alliance = alliances[allianceId];
    
    if (eventType == "betrayal") {
        alliance.trust *= 0.5f;
        alliance.strength *= 0.7f;
        
        if (alliance.trust < 0.2f) {
            breakAlliance(allianceId, "trust_broken");
        }
    }
    else if (eventType == "cooperation") {
        alliance.trust = std::min(alliance.trust + 0.1f, 1.0f);
        alliance.strength = std::min(alliance.strength + 0.05f, 1.0f);
        
        // Renforcer les liens
        for (const auto& familyId : alliance.memberFamilies) {
            auto& family = FamilyRelations::getInstance().getFamily(familyId);
            family.familyHonor = std::min(family.familyHonor + 0.05f, 1.0f);
        }
    }
    
    // Créer un souvenir de l'événement
    CollectiveMemoryEvent allianceEvent;
    allianceEvent.type = (eventType == "betrayal") ? MemoryType::NEGATIVE : MemoryType::POSITIVE;
    allianceEvent.importance = 0.8f;
    allianceEvent.description = "alliance_" + eventType;
    
    for (const auto& familyId : alliance.memberFamilies) {
        CollectiveMemory::getInstance().recordEvent(familyId, allianceEvent);
    }
}

void AllianceSystem::shareTraditions(const std::string& allianceId) {
    auto& alliance = alliances[allianceId];
    
    // Collecter toutes les traditions
    std::vector<std::string> allTraditions;
    for (const auto& familyId : alliance.memberFamilies) {
        auto& family = FamilyRelations::getInstance().getFamily(familyId);
        allTraditions.insert(allTraditions.end(), 
                           family.traditions.begin(), 
                           family.traditions.end());
    }
    
    // Partager les traditions
    for (const auto& familyId : alliance.memberFamilies) {
        auto& family = FamilyRelations::getInstance().getFamily(familyId);
        
        for (const auto& tradition : allTraditions) {
            if (std::find(family.traditions.begin(), 
                         family.traditions.end(), 
                         tradition) == family.traditions.end()) {
                // Nouvelle tradition pour cette famille
                family.traditions.push_back(tradition);
                
                // Organiser un rituel de transmission
                FamilyRelations::getInstance().passFamilyTradition(
                    familyId,
                    tradition
                );
            }
        }
    }
    
    // Renforcer l'alliance
    alliance.strength = std::min(alliance.strength + 0.1f, 1.0f);
    alliance.trust = std::min(alliance.trust + 0.05f, 1.0f);
}

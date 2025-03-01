#include "negotiation_system.h"
#include "natives.h"
#include "reputation_system.h"
#include "alliance_system.h"
#include "family_relations.h"
#include "collective_memory.h"

void NegotiationSystem::initializeNegotiation(const std::string& initiator, const std::string& target, NegotiationType type) {
    std::string negotiationId = initiator + "_" + target + "_" + std::to_string(MISC::GET_GAME_TIMER());
    
    NegotiationState negotiation;
    negotiation.negotiationId = negotiationId;
    negotiation.type = type;
    negotiation.stage = NegotiationStage::PROPOSED;
    negotiation.participants = {initiator, target};
    negotiation.tension = 0.3f;
    negotiation.progress = 0.0f;
    negotiation.deadline = MISC::GET_GAME_TIMER() + 3600000.0f; // 1 heure
    
    // Configurer selon le type
    switch (type) {
        case NegotiationType::ALLIANCE:
            negotiation.requiresMediator = false;
            // Termes de base pour une alliance
            {
                NegotiationTerm term;
                term.description = "mutual_protection";
                term.value = 0.7f;
                term.isNonNegotiable = true;
                term.beneficiary = "both";
                negotiation.terms.push_back(term);
            }
            break;
            
        case NegotiationType::PEACE:
            negotiation.requiresMediator = true;
            negotiation.tension = 0.8f;
            // Termes de base pour la paix
            {
                NegotiationTerm term;
                term.description = "cease_hostilities";
                term.value = 1.0f;
                term.isNonNegotiable = true;
                term.beneficiary = "both";
                negotiation.terms.push_back(term);
            }
            break;
    }
    
    activeNegotiations[negotiationId] = negotiation;
    
    // Mettre à jour les références des groupes
    groupNegotiations[initiator].push_back(negotiationId);
    groupNegotiations[target].push_back(negotiationId);
}

void NegotiationSystem::updateNegotiations() {
    for (auto& [negotiationId, negotiation] : activeNegotiations) {
        if (negotiation.stage == NegotiationStage::REJECTED ||
            negotiation.stage == NegotiationStage::ACCEPTED) {
            continue;
        }
        
        // Mettre à jour la progression
        updateNegotiationProgress(negotiation);
        
        // Gérer les délais
        handleDeadlines(negotiation);
        
        // Gérer les conflits d'intérêts
        manageConflictingInterests(negotiation);
        
        // Vérifier les conditions de fin
        if (negotiation.progress >= 1.0f) {
            negotiation.stage = NegotiationStage::ACCEPTED;
            finalizeNegotiation(negotiationId);
        } else if (negotiation.tension >= 1.0f) {
            negotiation.stage = NegotiationStage::REJECTED;
            handleFailedNegotiation(negotiationId);
        }
    }
}

void NegotiationSystem::updateNegotiationProgress(NegotiationState& negotiation) {
    float progressDelta = 0.0f;
    
    // Évaluer chaque terme
    for (const auto& term : negotiation.terms) {
        bool isAcceptable = true;
        for (const auto& participantId : negotiation.participants) {
            if (!isTermAcceptable(participantId, term)) {
                isAcceptable = false;
                break;
            }
        }
        
        if (isAcceptable) {
            progressDelta += 0.1f;
        } else {
            negotiation.tension += 0.05f;
        }
    }
    
    // Impact de la réputation
    float reputationFactor = 0.0f;
    for (const auto& participantId : negotiation.participants) {
        auto& family = FamilyRelations::getInstance().getFamily(participantId);
        reputationFactor += family.familyHonor;
    }
    reputationFactor /= negotiation.participants.size();
    
    progressDelta *= reputationFactor;
    
    // Mettre à jour la progression
    negotiation.progress = std::clamp(
        negotiation.progress + progressDelta,
        0.0f, 1.0f
    );
}

void NegotiationSystem::assignMediator(const std::string& negotiationId, const std::string& mediatorId) {
    auto& negotiation = activeNegotiations[negotiationId];
    
    if (!negotiation.requiresMediator) {
        return;
    }
    
    // Vérifier la réputation du médiateur
    auto& mediatorFamily = FamilyRelations::getInstance().getFamily(mediatorId);
    if (mediatorFamily.familyHonor < 0.7f) {
        return;
    }
    
    // Ajouter le médiateur
    negotiation.participants.push_back(mediatorId);
    
    // Réduire la tension
    negotiation.tension *= 0.8f;
    
    // Ajouter des termes de médiation
    NegotiationTerm mediationTerm;
    mediationTerm.description = "mediated_resolution";
    mediationTerm.value = 0.5f;
    mediationTerm.isNonNegotiable = true;
    mediationTerm.beneficiary = mediatorId;
    
    negotiation.terms.push_back(mediationTerm);
}

void NegotiationSystem::evaluateOffer(const std::string& negotiationId) {
    auto& negotiation = activeNegotiations[negotiationId];
    
    float totalValue = 0.0f;
    std::unordered_map<std::string, float> benefitsByParticipant;
    
    // Calculer la valeur pour chaque participant
    for (const auto& term : negotiation.terms) {
        if (term.beneficiary == "both") {
            for (const auto& participant : negotiation.participants) {
                benefitsByParticipant[participant] += term.value;
            }
        } else {
            benefitsByParticipant[term.beneficiary] += term.value;
        }
        
        if (term.provider != "") {
            benefitsByParticipant[term.provider] -= term.value * 0.8f;
        }
        
        totalValue += term.value;
    }
    
    // Vérifier l'équilibre
    float minBenefit = std::numeric_limits<float>::max();
    float maxBenefit = std::numeric_limits<float>::lowest();
    
    for (const auto& [participant, benefit] : benefitsByParticipant) {
        minBenefit = std::min(minBenefit, benefit);
        maxBenefit = std::max(maxBenefit, benefit);
    }
    
    // Ajuster la tension selon l'équilibre
    float imbalance = maxBenefit - minBenefit;
    if (imbalance > 0.5f) {
        negotiation.tension += imbalance * 0.2f;
    } else {
        negotiation.progress += 0.1f;
    }
}

bool NegotiationSystem::isTermAcceptable(const std::string& groupId, const NegotiationTerm& term) {
    auto& family = FamilyRelations::getInstance().getFamily(groupId);
    
    // Vérifier si le terme est non négociable
    if (term.isNonNegotiable) {
        return true;
    }
    
    // Calculer la valeur relative
    float relativeValue = term.value;
    if (term.provider == groupId) {
        relativeValue *= -1.0f;
    }
    
    // Facteurs d'acceptabilité
    float acceptabilityThreshold = 0.3f;
    
    // Modifier le seuil selon l'honneur familial
    acceptabilityThreshold += family.familyHonor * 0.2f;
    
    // Modifier selon les alliances existantes
    for (const auto& allianceId : AllianceSystem::getInstance().getGroupAlliances(groupId)) {
        auto& alliance = AllianceSystem::getInstance().getAlliance(allianceId);
        if (alliance.trust > 0.7f) {
            acceptabilityThreshold -= 0.1f;
        }
    }
    
    // Vérifier les souvenirs collectifs
    auto recentMemories = CollectiveMemory::getInstance().getRecentMemories(groupId, 5);
    for (const auto& memory : recentMemories) {
        if (memory.type == MemoryType::NEGATIVE) {
            acceptabilityThreshold += 0.1f;
        } else {
            acceptabilityThreshold -= 0.05f;
        }
    }
    
    return relativeValue >= acceptabilityThreshold;
}

void NegotiationSystem::handleDeadlines(NegotiationState& negotiation) {
    float currentTime = MISC::GET_GAME_TIMER();
    
    if (currentTime > negotiation.deadline) {
        // Augmenter la tension près de la deadline
        float timeRemaining = negotiation.deadline - currentTime;
        if (timeRemaining < 600000.0f) { // 10 minutes
            negotiation.tension += 0.1f;
        }
    }
}

void NegotiationSystem::manageConflictingInterests(NegotiationState& negotiation) {
    // Vérifier les conflits entre termes
    for (size_t i = 0; i < negotiation.terms.size(); i++) {
        for (size_t j = i + 1; j < negotiation.terms.size(); j++) {
            const auto& term1 = negotiation.terms[i];
            const auto& term2 = negotiation.terms[j];
            
            // Détecter les conflits
            if (term1.beneficiary == term2.provider ||
                term2.beneficiary == term1.provider) {
                negotiation.tension += 0.05f;
            }
        }
    }
    
    // Gérer les alliances existantes
    for (const auto& participantId : negotiation.participants) {
        auto alliances = AllianceSystem::getInstance().getGroupAlliances(participantId);
        for (const auto& allianceId : alliances) {
            auto& alliance = AllianceSystem::getInstance().getAlliance(allianceId);
            
            // Vérifier si les termes violent des obligations d'alliance
            for (const auto& obligation : alliance.terms.obligations) {
                bool violatesObligation = false;
                // Vérifier chaque terme
                for (const auto& term : negotiation.terms) {
                    if (term.description == obligation) {
                        violatesObligation = true;
                        break;
                    }
                }
                
                if (violatesObligation) {
                    negotiation.tension += 0.1f;
                }
            }
        }
    }
}

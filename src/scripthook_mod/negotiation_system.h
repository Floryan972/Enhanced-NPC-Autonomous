#pragma once
#include "types.h"
#include <unordered_map>
#include <vector>
#include <string>

enum class NegotiationType {
    ALLIANCE,
    TRADE,
    PEACE,
    TERRITORY,
    MARRIAGE,
    RESOURCES
};

enum class NegotiationStage {
    PROPOSED,
    DISCUSSING,
    BARGAINING,
    FINALIZING,
    ACCEPTED,
    REJECTED
};

struct NegotiationTerm {
    std::string description;
    float value;
    bool isNonNegotiable;
    std::string beneficiary;
    std::string provider;
};

struct NegotiationState {
    std::string negotiationId;
    NegotiationType type;
    NegotiationStage stage;
    std::vector<std::string> participants;
    std::vector<NegotiationTerm> terms;
    float tension;
    float progress;
    float deadline;
    bool requiresMediator;
};

class NegotiationSystem {
public:
    static NegotiationSystem& getInstance() {
        static NegotiationSystem instance;
        return instance;
    }

    void initializeNegotiation(const std::string& initiator, const std::string& target, NegotiationType type);
    void updateNegotiations();
    void proposeTerm(const std::string& negotiationId, const NegotiationTerm& term);
    void respondToProposal(const std::string& negotiationId, bool accept);
    
    // Nouvelles fonctions de négociation
    void assignMediator(const std::string& negotiationId, const std::string& mediatorId);
    void adjustTerms(const std::string& negotiationId, const std::vector<NegotiationTerm>& adjustments);
    void evaluateOffer(const std::string& negotiationId);
    bool isTermAcceptable(const std::string& groupId, const NegotiationTerm& term);

private:
    NegotiationSystem() {}
    std::unordered_map<std::string, NegotiationState> activeNegotiations;
    std::unordered_map<std::string, std::vector<std::string>> groupNegotiations;
    
    void updateNegotiationProgress(NegotiationState& negotiation);
    void handleDeadlines(NegotiationState& negotiation);
    void manageConflictingInterests(NegotiationState& negotiation);
    void calculateBargainingPower(const std::string& groupId);
};

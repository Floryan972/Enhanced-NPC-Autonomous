#include "group_learning.h"
#include "natives.h"
#include "social_group_system.h"
#include "collective_memory.h"
#include "personality_system.h"
#include "event_manager.h"

void GroupLearning::initializeGroupLearning(const std::string& groupId) {
    GroupKnowledge& knowledge = groupKnowledge[groupId];
    knowledge.adaptabilityScore = 0.5f;
    knowledge.generationCount = 1;

    // Comportements de base
    LearnedBehavior combatBehavior;
    combatBehavior.category = LearningCategory::COMBAT;
    combatBehavior.successRate = 0.5f;
    combatBehavior.timesUsed = 0;
    knowledge.behaviors["basic_combat"] = combatBehavior;

    LearnedBehavior survivalBehavior;
    survivalBehavior.category = LearningCategory::SURVIVAL;
    survivalBehavior.successRate = 0.5f;
    survivalBehavior.timesUsed = 0;
    knowledge.behaviors["basic_survival"] = survivalBehavior;
}

void GroupLearning::recordBehaviorOutcome(const std::string& groupId, const std::string& behaviorId, bool success) {
    auto& knowledge = groupKnowledge[groupId];
    auto& behavior = knowledge.behaviors[behaviorId];
    
    // Mettre à jour les statistiques
    behavior.timesUsed++;
    float learningRate = 0.1f;
    behavior.successRate = (behavior.successRate * (1.0f - learningRate)) + 
                         (success ? learningRate : 0.0f);

    // Mettre à jour l'efficacité
    behavior.effectiveness = (behavior.effectiveness * behavior.timesUsed + 
                           (success ? 1.0f : 0.0f)) / (behavior.timesUsed + 1);

    // Adapter le score d'adaptabilité du groupe
    knowledge.adaptabilityScore = (knowledge.adaptabilityScore * 0.9f) + 
                                (success ? 0.1f : -0.05f);
    knowledge.adaptabilityScore = std::clamp(knowledge.adaptabilityScore, 0.0f, 1.0f);
}

void GroupLearning::evolveTactics(const std::string& groupId) {
    auto& knowledge = groupKnowledge[groupId];
    
    // Évaluer les comportements existants
    for (auto& [behaviorId, behavior] : knowledge.behaviors) {
        if (behavior.timesUsed > 10 && behavior.successRate < 0.3f) {
            // Modifier le comportement
            switch (behavior.category) {
                case LearningCategory::COMBAT:
                    // Essayer une approche plus défensive
                    behavior.effectiveness *= 0.8f;
                    break;
                case LearningCategory::SURVIVAL:
                    // Améliorer la recherche de ressources
                    behavior.effectiveness *= 0.9f;
                    break;
                case LearningCategory::TERRITORY:
                    // Ajuster la stratégie territoriale
                    behavior.effectiveness *= 0.85f;
                    break;
            }
        }
    }

    // Générer de nouvelles stratégies
    generateNewStrategies(groupId);

    // Incrémenter la génération
    knowledge.generationCount++;
}

void GroupLearning::generateNewStrategies(const std::string& groupId) {
    auto& knowledge = groupKnowledge[groupId];
    
    // Créer de nouvelles stratégies basées sur les plus efficaces
    std::vector<std::pair<std::string, float>> successfulBehaviors;
    
    for (const auto& [behaviorId, behavior] : knowledge.behaviors) {
        if (behavior.successRate > 0.7f && behavior.timesUsed > 5) {
            successfulBehaviors.push_back({behaviorId, behavior.successRate});
        }
    }

    // Combiner les comportements réussis
    for (size_t i = 0; i < successfulBehaviors.size(); i++) {
        for (size_t j = i + 1; j < successfulBehaviors.size(); j++) {
            std::string newBehaviorId = "evolved_" + 
                                      successfulBehaviors[i].first + "_" + 
                                      successfulBehaviors[j].first;
            
            LearnedBehavior newBehavior;
            newBehavior.category = knowledge.behaviors[successfulBehaviors[i].first].category;
            newBehavior.successRate = (successfulBehaviors[i].second + 
                                     successfulBehaviors[j].second) / 2.0f;
            newBehavior.timesUsed = 0;
            
            knowledge.behaviors[newBehaviorId] = newBehavior;
        }
    }
}

void GroupLearning::learnFromEvents(const std::string& groupId, const CollectiveMemoryEvent& event) {
    auto& knowledge = groupKnowledge[groupId];
    
    // Créer un nouveau comportement basé sur l'événement
    LearnedBehavior newBehavior;
    newBehavior.lastLocation = event.location;
    
    switch (event.type) {
        case MemoryType::THREAT:
            newBehavior.category = LearningCategory::SURVIVAL;
            break;
        case MemoryType::POSITIVE:
            newBehavior.category = LearningCategory::SOCIAL;
            break;
        case MemoryType::ALLIANCE:
            newBehavior.category = LearningCategory::TACTICS;
            break;
    }

    // Identifier les NPCs qui peuvent enseigner ce comportement
    for (Ped ped : event.involvedPeds) {
        if (ENTITY::DOES_ENTITY_EXIST(ped)) {
            auto* personality = PersonalitySystem::getInstance().getPersonality(ped);
            if (personality && personality->intelligence > 0.7f) {
                newBehavior.teachingPeds.push_back(ped);
            }
        }
    }

    // Ajouter le nouveau comportement
    std::string behaviorId = "learned_from_event_" + std::to_string(event.timeStamp);
    knowledge.behaviors[behaviorId] = newBehavior;
}

void GroupLearning::teachBehavior(Ped teacher, Ped student, const std::string& behaviorId) {
    // Vérifier si l'enseignant est qualifié
    std::string teacherGroupId = SocialGroupSystem::getInstance().getGroupId(teacher);
    auto& knowledge = groupKnowledge[teacherGroupId];
    
    if (knowledge.teacherRatings[teacher] > 0.6f) {
        auto& behavior = knowledge.behaviors[behaviorId];
        
        // Transférer le comportement
        switch (behavior.category) {
            case LearningCategory::COMBAT:
                // Enseigner des tactiques de combat
                AI::TASK_COMBAT_PED(student, teacher, 0, 16);
                break;
            case LearningCategory::SURVIVAL:
                // Enseigner des techniques de survie
                AI::TASK_FOLLOW_TO_OFFSET_OF_ENTITY(
                    student, teacher, 0.0f, -1.0f, 0.0f, 
                    1.0f, -1, 2.0f, true
                );
                break;
            case LearningCategory::TERRITORY:
                // Montrer les points stratégiques
                AI::TASK_GO_TO_COORD_ANY_MEANS(
                    student,
                    behavior.lastLocation.x,
                    behavior.lastLocation.y,
                    behavior.lastLocation.z,
                    2.0f, 0, 0, 786603, 0xbf800000
                );
                break;
        }

        // Mettre à jour le rating de l'enseignant
        knowledge.teacherRatings[teacher] += 0.1f;
    }
}

void GroupLearning::adaptToEnvironment(const std::string& groupId, const Vector3& location) {
    auto& knowledge = groupKnowledge[groupId];
    
    // Analyser l'environnement
    bool isIndoors = INTERIOR::GET_INTERIOR_FROM_ENTITY(PLAYER::PLAYER_PED_ID()) != 0;
    Hash weatherHash = MISC::GET_PREV_WEATHER_TYPE_HASH_NAME();
    
    // Adapter les comportements existants
    for (auto& [behaviorId, behavior] : knowledge.behaviors) {
        if (behavior.category == LearningCategory::SURVIVAL) {
            // Adapter aux conditions météorologiques
            adaptBehaviorToWeather(behavior, MISC::GET_PREV_WEATHER_TYPE_HASH_NAME());
        }
        
        if (behavior.category == LearningCategory::TERRITORY) {
            // Mémoriser les bons abris
            if (isIndoors) {
                behavior.lastLocation = location;
                behavior.effectiveness += 0.1f;
            }
        }
    }

    // Mettre à jour les emplacements stratégiques
    if (knowledge.adaptabilityScore > 0.7f) {
        knowledge.strategicLocations.push_back(location);
    }
}

void GroupLearning::adaptBehaviorToWeather(LearnedBehavior& behavior, const std::string& weatherType) {
    if (weatherType == "RAIN" || weatherType == "THUNDER") {
        // Augmenter l'importance des abris
        behavior.effectiveness *= 1.2f;
    } else if (weatherType == "CLEAR") {
        // Favoriser l'exploration
        behavior.effectiveness *= 0.9f;
    }
    
    behavior.effectiveness = std::clamp(behavior.effectiveness, 0.0f, 1.0f);
}

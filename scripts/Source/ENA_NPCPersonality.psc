Scriptname ENA_NPCPersonality extends Quest
{Manages NPC personalities, traits, and backgrounds}

; Import required game systems
import Game
import Debug
import Utility
import Actor

; Enums and Structs
Struct Personality
    String[] traits ; RUTHLESS, CAUTIOUS, LOYAL, TREACHEROUS, etc.
    float[] traitValues
    String dominantTrait
    bool isStable
EndStruct

Struct Background
    String origin
    String[] lifeEvents
    ActorBase[] family
    String motivation
    bool isTraumatic
EndStruct

Struct Relationship
    ActorBase npc1
    ActorBase npc2
    String type ; FAMILY, FRIEND, RIVAL, MENTOR, etc.
    float strength
    bool isPositive
EndStruct

Struct PersonalGoal
    String objective
    float progress
    float priority
    String[] requirements
    bool isAchievable
EndStruct

; Properties
Personality[] Property NPCPersonalities Auto
Background[] Property NPCBackgrounds Auto
Relationship[] Property NPCRelationships Auto
float Property UpdateInterval = 5.0 Auto

; Events
Event OnInit()
    Initialize()
    RegisterForUpdateGameTime(UpdateInterval)
EndEvent

Event OnUpdateGameTime()
    UpdatePersonalities()
EndEvent

; Core functions
Function Initialize()
    InitializePersonalitySystem()
    SetupInitialBackgrounds()
EndFunction

Function InitializePersonalitySystem()
    ; Setup personality traits
    CreatePersonalityTraits()
    
    ; Setup backgrounds
    InitializeBackgrounds()
    
    ; Setup relationships
    InitializeRelationships()
EndFunction

; Personality management
Function CreatePersonality(ActorBase npc)
    Personality personality = new Personality
    
    ; Generate traits
    personality.traits = GenerateTraits()
    
    ; Set trait values
    personality.traitValues = GenerateTraitValues()
    
    ; Determine dominant trait
    personality.dominantTrait = DetermineDominantTrait(personality)
    
    NPCPersonalities.Add(personality)
EndFunction

Function UpdatePersonality(Personality personality)
    ; Update trait values
    UpdateTraitValues(personality)
    
    ; Check stability
    CheckPersonalityStability(personality)
    
    ; Handle changes
    HandlePersonalityChanges(personality)
    
    ; Update dominant trait
    UpdateDominantTrait(personality)
EndFunction

; Background management
Function CreateBackground(ActorBase npc)
    Background background = new Background
    
    ; Generate origin
    background.origin = GenerateOrigin()
    
    ; Create life events
    background.lifeEvents = GenerateLifeEvents()
    
    ; Generate family
    background.family = GenerateFamily(npc)
    
    ; Set motivation
    background.motivation = DetermineMotivation(background)
    
    NPCBackgrounds.Add(background)
EndFunction

Function UpdateBackground(Background background)
    ; Add new events
    UpdateLifeEvents(background)
    
    ; Update family
    UpdateFamilyRelations(background)
    
    ; Update motivation
    UpdateMotivation(background)
EndFunction

; Relationship management
Function CreateRelationship(ActorBase npc1, ActorBase npc2, String type)
    Relationship relationship = new Relationship
    relationship.npc1 = npc1
    relationship.npc2 = npc2
    relationship.type = type
    
    ; Set initial strength
    relationship.strength = CalculateInitialStrength(type)
    
    ; Determine nature
    relationship.isPositive = DetermineRelationshipNature(npc1, npc2)
    
    NPCRelationships.Add(relationship)
EndFunction

Function UpdateRelationship(Relationship relationship)
    ; Update strength
    UpdateRelationshipStrength(relationship)
    
    ; Handle conflicts
    HandleRelationshipConflicts(relationship)
    
    ; Update nature
    UpdateRelationshipNature(relationship)
EndFunction

; Goal management
Function CreatePersonalGoal(ActorBase npc)
    PersonalGoal goal = new PersonalGoal
    
    ; Set objective
    goal.objective = DetermineObjective(npc)
    
    ; Set requirements
    goal.requirements = SetGoalRequirements(goal.objective)
    
    ; Calculate priority
    goal.priority = CalculateGoalPriority(goal)
    
    ; Check achievability
    goal.isAchievable = AssessGoalAchievability(goal)
EndFunction

Function UpdateGoal(PersonalGoal goal)
    ; Update progress
    UpdateGoalProgress(goal)
    
    ; Adjust priority
    AdjustGoalPriority(goal)
    
    ; Check requirements
    CheckGoalRequirements(goal)
    
    ; Update achievability
    UpdateGoalAchievability(goal)
EndFunction

; Trait influence
Function ApplyTraitInfluence(Personality personality, String action)
    String dominantTrait = personality.dominantTrait
    
    if dominantTrait == "RUTHLESS"
        ApplyRuthlessInfluence(action)
    elseif dominantTrait == "CAUTIOUS"
        ApplyCautiousInfluence(action)
    elseif dominantTrait == "LOYAL"
        ApplyLoyalInfluence(action)
    endif
EndFunction

Function HandleTraitConflict(Personality personality)
    ; Identify conflicting traits
    String[] conflicts = FindTraitConflicts(personality)
    
    ; Resolve conflicts
    ResolveTraitConflicts(personality, conflicts)
    
    ; Update trait values
    UpdateConflictingTraits(personality, conflicts)
EndFunction

; Emotional system
Function ProcessEmotionalResponse(ActorBase npc, String event)
    Personality personality = GetNPCPersonality(npc)
    
    ; Calculate response
    String response = CalculateEmotionalResponse(personality, event)
    
    ; Apply effects
    ApplyEmotionalEffects(npc, response)
    
    ; Update personality
    UpdatePersonalityFromEmotion(personality, response)
EndFunction

Function ManageStressLevel(ActorBase npc)
    ; Calculate stress
    float stress = CalculateNPCStress(npc)
    
    ; Apply effects
    ApplyStressEffects(npc, stress)
    
    ; Handle breakdown
    if stress > 0.9
        TriggerMentalBreakdown(npc)
    endif
EndFunction

; Memory system
Function AddMemory(ActorBase npc, String event)
    ; Record event
    RecordMemory(npc, event)
    
    ; Calculate impact
    float impact = CalculateMemoryImpact(event)
    
    ; Apply effects
    ApplyMemoryEffects(npc, event, impact)
    
    ; Update relationships
    UpdateRelationshipsFromMemory(npc, event)
EndFunction

Function ProcessTrauma(Background background)
    if background.isTraumatic
        ; Handle trauma
        HandleTraumaticBackground(background)
        
        ; Apply effects
        ApplyTraumaEffects(background)
        
        ; Update motivation
        UpdateTraumaMotivation(background)
    endif
EndFunction

; Utility functions
bool Function HasPersonality(ActorBase actor)
    return actor && actor.HasKeyword(Game.GetForm("PersonalityKeyword") as Keyword)
EndFunction

Function UpdatePersonalities()
    ; Update all personalities
    int i = 0
    while i < NPCPersonalities.Length
        Personality personality = NPCPersonalities[i]
        
        ; Update personality
        UpdatePersonality(personality)
        
        ; Process emotions
        ProcessEmotions(personality)
        
        ; Update goals
        UpdatePersonalGoals(personality)
        
        ; Handle relationships
        UpdatePersonalRelationships(personality)
        
        i += 1
    endwhile
    
    ; Update backgrounds
    UpdateNPCBackgrounds()
EndFunction

Scriptname ENA_NPCRoutines extends Quest
{Manages NPC daily routines, preferences, and skills}

; Import required game systems
import Game
import Debug
import Utility
import Actor

; Enums and Structs
Struct DailyRoutine
    String[] activities
    Location[] locations
    float[] timeSlots ; 24-hour format
    ActorBase[] contacts
    bool isFlexible
EndStruct

Struct NPCPreference
    String[] likes
    String[] dislikes
    Form[] favoriteItems
    Location[] favoriteLocations
    bool isStrong
EndStruct

Struct Skill
    String name
    float level ; 0.0 to 1.0
    float experience
    String[] specializations
    bool canTeach
EndStruct

Struct Hobby
    String activity
    float enthusiasm
    Form[] equipment
    Location[] venues
    bool isSecret
EndStruct

; Properties
DailyRoutine[] Property NPCRoutines Auto
NPCPreference[] Property NPCPreferences Auto
Skill[] Property NPCSkills Auto
float Property UpdateInterval = 1.0 Auto

; Events
Event OnInit()
    Initialize()
    RegisterForUpdateGameTime(UpdateInterval)
EndEvent

Event OnUpdateGameTime()
    UpdateRoutines()
EndEvent

; Core functions
Function Initialize()
    InitializeRoutineSystem()
    SetupInitialPreferences()
EndFunction

Function InitializeRoutineSystem()
    ; Setup routines
    CreateInitialRoutines()
    
    ; Setup preferences
    InitializePreferences()
    
    ; Setup skills
    InitializeSkills()
EndFunction

; Routine management
Function CreateDailyRoutine(ActorBase npc)
    DailyRoutine routine = new DailyRoutine
    
    ; Set activities
    routine.activities = GenerateActivities(npc)
    
    ; Assign locations
    routine.locations = AssignLocations(routine.activities)
    
    ; Set time slots
    routine.timeSlots = AssignTimeSlots(routine.activities)
    
    ; Add contacts
    routine.contacts = AssignDailyContacts(npc)
    
    NPCRoutines.Add(routine)
EndFunction

Function UpdateRoutine(DailyRoutine routine)
    ; Update activities
    UpdateDailyActivities(routine)
    
    ; Update locations
    UpdateRoutineLocations(routine)
    
    ; Adjust time slots
    AdjustTimeSlots(routine)
    
    ; Update contacts
    UpdateDailyContacts(routine)
EndFunction

; Preference management
Function CreatePreferences(ActorBase npc)
    NPCPreference preference = new NPCPreference
    
    ; Generate likes/dislikes
    preference.likes = GenerateLikes(npc)
    preference.dislikes = GenerateDislikes(npc)
    
    ; Set favorite items
    preference.favoriteItems = SetFavoriteItems(npc)
    
    ; Set locations
    preference.favoriteLocations = SetFavoriteLocations(npc)
    
    NPCPreferences.Add(preference)
EndFunction

Function UpdatePreferences(NPCPreference preference)
    ; Update likes/dislikes
    UpdatePreferenceList(preference)
    
    ; Update favorites
    UpdateFavorites(preference)
    
    ; Handle changes
    HandlePreferenceChanges(preference)
EndFunction

; Skill management
Function CreateSkill(String name, ActorBase npc)
    Skill skill = new Skill
    skill.name = name
    
    ; Set initial level
    skill.level = CalculateInitialLevel(npc, name)
    
    ; Set experience
    skill.experience = 0.0
    
    ; Set specializations
    skill.specializations = DetermineSpecializations(name)
    
    NPCSkills.Add(skill)
EndFunction

Function UpdateSkill(Skill skill)
    ; Update level
    UpdateSkillLevel(skill)
    
    ; Add experience
    AddSkillExperience(skill)
    
    ; Update specializations
    UpdateSpecializations(skill)
    
    ; Check teaching ability
    UpdateTeachingAbility(skill)
EndFunction

; Hobby management
Function CreateHobby(ActorBase npc)
    Hobby hobby = new Hobby
    
    ; Choose activity
    hobby.activity = ChooseHobbyActivity(npc)
    
    ; Set enthusiasm
    hobby.enthusiasm = CalculateInitialEnthusiasm()
    
    ; Assign equipment
    hobby.equipment = AssignHobbyEquipment(hobby.activity)
    
    ; Find venues
    hobby.venues = FindHobbyVenues(hobby.activity)
EndFunction

Function UpdateHobby(Hobby hobby)
    ; Update enthusiasm
    UpdateHobbyEnthusiasm(hobby)
    
    ; Update equipment
    UpdateHobbyEquipment(hobby)
    
    ; Find new venues
    UpdateHobbyVenues(hobby)
EndFunction

; Activity scheduling
Function ScheduleActivity(DailyRoutine routine, String activity, float time)
    ; Check time slot
    if IsTimeSlotAvailable(routine, time)
        ; Add activity
        AddScheduledActivity(routine, activity, time)
        
        ; Assign location
        AssignActivityLocation(routine, activity)
        
        ; Update contacts
        UpdateActivityContacts(routine, activity)
    endif
EndFunction

Function HandleActivityConflict(DailyRoutine routine, String activity1, String activity2)
    ; Calculate priorities
    float priority1 = CalculateActivityPriority(activity1)
    float priority2 = CalculateActivityPriority(activity2)
    
    ; Resolve conflict
    if priority1 > priority2
        RescheduleActivity(routine, activity2)
    else
        RescheduleActivity(routine, activity1)
    endif
EndFunction

; Skill development
Function DevelopSkill(Skill skill, float amount)
    ; Add experience
    skill.experience += amount
    
    ; Check for level up
    if ShouldLevelUp(skill)
        LevelUpSkill(skill)
        
        ; Update specializations
        UpdateSkillSpecializations(skill)
        
        ; Check teaching
        UpdateTeachingStatus(skill)
    endif
EndFunction

Function TeachSkill(ActorBase teacher, ActorBase student, Skill skill)
    if skill.canTeach
        ; Calculate effectiveness
        float effectiveness = CalculateTeachingEffectiveness(teacher, student)
        
        ; Transfer knowledge
        TransferSkillKnowledge(teacher, student, skill, effectiveness)
        
        ; Update relationship
        UpdateTeachingRelationship(teacher, student)
    endif
EndFunction

; Preference influence
Function ApplyPreferences(ActorBase npc, String action)
    NPCPreference preference = GetNPCPreferences(npc)
    
    ; Check against preferences
    if IsPreferred(preference, action)
        ApplyPreferenceBonus(npc, action)
    else
        ApplyPreferencePenalty(npc, action)
    endif
EndFunction

Function UpdatePreferenceStrength(NPCPreference preference, String item, bool positive)
    if positive
        IncreasePreferenceStrength(preference, item)
    else
        DecreasePreferenceStrength(preference, item)
    endif
EndFunction

; Routine flexibility
Function AdjustRoutineFlexibility(DailyRoutine routine)
    ; Calculate stress
    float stress = CalculateRoutineStress(routine)
    
    ; Adjust flexibility
    routine.isFlexible = (stress < 0.7)
    
    ; Update schedule
    if routine.isFlexible
        OptimizeRoutine(routine)
    endif
EndFunction

Function HandleRoutineDisruption(DailyRoutine routine, String cause)
    if routine.isFlexible
        ; Adapt routine
        AdaptRoutine(routine, cause)
    else
        ; Handle stress
        HandleRoutineStress(routine)
        
        ; Force adaptation
        ForceRoutineAdaptation(routine)
    endif
EndFunction

; Utility functions
bool Function HasRoutine(ActorBase actor)
    return actor && actor.HasKeyword(Game.GetForm("RoutineKeyword") as Keyword)
EndFunction

Function UpdateRoutines()
    ; Update all routines
    int i = 0
    while i < NPCRoutines.Length
        DailyRoutine routine = NPCRoutines[i]
        
        ; Update routine
        UpdateRoutine(routine)
        
        ; Update preferences
        UpdateNPCPreferences(routine)
        
        ; Update skills
        UpdateNPCSkills(routine)
        
        ; Update hobbies
        UpdateNPCHobbies(routine)
        
        i += 1
    endwhile
EndFunction

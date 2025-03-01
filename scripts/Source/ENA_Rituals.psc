Scriptname ENA_Rituals extends Quest
{Handles group rituals and ceremonies}

; Import required game systems
import Game
import Debug
import Utility
import Actor

; Enums and Structs
Struct Ritual
    String name
    String type
    float duration
    float importance
    ObjectReference location
    Actor[] participants
    Form[] requiredItems
    String[] animations
EndStruct

; Properties
Ritual[] Property ActiveRituals Auto
float Property UpdateInterval = 1.0 Auto

; Events
Event OnInit()
    Initialize()
EndEvent

Event OnUpdate()
    UpdateRituals()
EndEvent

; Core functions
Function Initialize()
    ActiveRituals = new Ritual[0]
    RegisterForUpdate(UpdateInterval)
EndFunction

Function Update()
    UpdateRituals()
    CheckForNewRituals()
    CleanupCompletedRituals()
EndFunction

; Ritual management
Function StartRitual(String ritualType, ObjectReference akLocation)
    Ritual newRitual = CreateRitual(ritualType)
    newRitual.location = akLocation
    
    ; Find participants
    Actor[] nearbyNPCs = GetNearbyActors(akLocation, 1000.0)
    newRitual.participants = FilterEligibleParticipants(nearbyNPCs, ritualType)
    
    ; Start the ritual
    if newRitual.participants.Length > 0
        ActiveRituals.Add(newRitual)
        NotifyRitualStart(newRitual)
        AssignRitualRoles(newRitual)
    endif
EndFunction

Ritual Function CreateRitual(String ritualType)
    Ritual ritual = new Ritual
    
    ; Configure based on type
    if ritualType == "INITIATION"
        ritual.name = "Initiation Ceremony"
        ritual.type = ritualType
        ritual.duration = 300.0 ; 5 minutes
        ritual.importance = 0.8
        ritual.animations = new String[3]
        ritual.animations[0] = "IdleRitualStart"
        ritual.animations[1] = "IdleRitualLoop"
        ritual.animations[2] = "IdleRitualEnd"
    elseif ritualType == "CELEBRATION"
        ritual.name = "Group Celebration"
        ritual.type = ritualType
        ritual.duration = 600.0 ; 10 minutes
        ritual.importance = 0.6
        ritual.animations = new String[2]
        ritual.animations[0] = "IdleCelebrate"
        ritual.animations[1] = "IdleDance"
    endif
    
    return ritual
EndFunction

Function UpdateRituals()
    int i = 0
    while i < ActiveRituals.Length
        Ritual ritual = ActiveRituals[i]
        
        ; Update participant positions and animations
        UpdateRitualParticipants(ritual)
        
        ; Check for completion
        if IsRitualComplete(ritual)
            CompleteRitual(ritual)
            ActiveRituals.Remove(i)
        else
            i += 1
        endif
    endwhile
EndFunction

Function UpdateRitualParticipants(Ritual ritual)
    int i = 0
    while i < ritual.participants.Length
        Actor participant = ritual.participants[i]
        
        if IsValidParticipant(participant)
            ; Update position
            float angle = (360.0 * i) / ritual.participants.Length
            float radius = 100.0 ; Distance from center
            
            float xOffset = Math.cos(angle) * radius
            float yOffset = Math.sin(angle) * radius
            
            ; Move participant
            participant.MoveTo(ritual.location, xOffset, yOffset, 0.0)
            
            ; Play animation
            String animation = ritual.animations[i % ritual.animations.Length]
            participant.PlayIdle(Game.GetForm(animation) as Idle)
        endif
        
        i += 1
    endwhile
EndFunction

; Utility functions
Actor[] Function GetNearbyActors(ObjectReference akCenter, float radius)
    Actor[] result = new Actor[0]
    Actor[] allActors = Game.GetAllActors()
    
    int i = 0
    while i < allActors.Length
        Actor current = allActors[i]
        if current.GetDistance(akCenter) <= radius
            result.Add(current)
        endif
        i += 1
    endwhile
    
    return result
EndFunction

Actor[] Function FilterEligibleParticipants(Actor[] actors, String ritualType)
    Actor[] eligible = new Actor[0]
    
    int i = 0
    while i < actors.Length
        Actor current = actors[i]
        if IsEligibleForRitual(current, ritualType)
            eligible.Add(current)
        endif
        i += 1
    endwhile
    
    return eligible
EndFunction

bool Function IsEligibleForRitual(Actor akActor, String ritualType)
    ; Basic eligibility checks
    if !akActor || akActor.IsDead() || akActor.IsDisabled()
        return false
    endif
    
    ; Specific ritual requirements
    if ritualType == "INITIATION"
        ; Check if actor is new to the group
        return true ; Add specific conditions
    elseif ritualType == "CELEBRATION"
        ; Anyone can participate in celebrations
        return true
    endif
    
    return false
EndFunction

bool Function IsValidParticipant(Actor akActor)
    return akActor && !akActor.IsDead() && !akActor.IsDisabled()
EndFunction

bool Function IsRitualComplete(Ritual ritual)
    return Utility.GetCurrentGameTime() >= (ritual.startTime + ritual.duration)
EndFunction

; Effects and feedback
Function NotifyRitualStart(Ritual ritual)
    Debug.Notification("A " + ritual.name + " has begun!")
    
    ; Visual effects
    Game.GetPlayer().PlaceAtMe(Game.GetForm("RitualEffect") as Form)
    
    ; Sound effects
    Game.GetPlayer().PlayIdle(Game.GetForm("RitualStartSound") as Idle)
EndFunction

Function CompleteRitual(Ritual ritual)
    Debug.Notification(ritual.name + " has been completed!")
    
    ; Apply ritual effects
    ApplyRitualEffects(ritual)
    
    ; Update participant relationships
    UpdateParticipantRelationships(ritual)
EndFunction

Function ApplyRitualEffects(Ritual ritual)
    int i = 0
    while i < ritual.participants.Length
        Actor participant = ritual.participants[i]
        
        if IsValidParticipant(participant)
            ; Apply buffs or effects based on ritual type
            if ritual.type == "INITIATION"
                ; Add initiation effects
                participant.ModActorValue("Confidence", 10)
            elseif ritual.type == "CELEBRATION"
                ; Add celebration effects
                participant.ModActorValue("Happiness", 15)
            endif
        endif
        
        i += 1
    endwhile
EndFunction

Function UpdateParticipantRelationships(Ritual ritual)
    int i = 0
    while i < ritual.participants.Length
        Actor participant1 = ritual.participants[i]
        
        int j = i + 1
        while j < ritual.participants.Length
            Actor participant2 = ritual.participants[j]
            
            ; Improve relationship between participants
            participant1.ModRelationshipRank(participant2, 1)
            
            j += 1
        endwhile
        
        i += 1
    endwhile
EndFunction

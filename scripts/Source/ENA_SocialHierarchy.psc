Scriptname ENA_SocialHierarchy extends Quest
{Handles social hierarchy and relationships between NPCs}

; Import required game systems
import Game
import Debug
import Actor

; Enums and Structs
String[] Property RankNames Auto
{LEADER, ELDER, MEMBER, etc.}

Struct SocialRole
    String name
    int authority
    bool isTemporary
    float duration
EndStruct

; Properties
Actor[] Property GroupLeaders Auto
float Property UpdateInterval = 5.0 Auto

; Events
Event OnInit()
    Initialize()
EndEvent

; Core functions
Function Initialize()
    InitializeRanks()
    InitializeRoles()
EndFunction

Function Update()
    UpdateHierarchy()
    UpdateRelationships()
    HandlePowerStruggles()
EndFunction

; Hierarchy management
Function InitializeRanks()
    RankNames = new String[5]
    RankNames[0] = "LEADER"
    RankNames[1] = "ELDER"
    RankNames[2] = "MEMBER"
    RankNames[3] = "INITIATE"
    RankNames[4] = "OUTSIDER"
EndFunction

Function UpdateHierarchy()
    Actor[] npcs = Game.GetAllActors()
    
    int i = 0
    while i < npcs.Length
        Actor npc = npcs[i]
        if IsValidNPC(npc)
            UpdateNPCRank(npc)
            UpdateNPCAuthority(npc)
        endif
        i += 1
    endwhile
EndFunction

Function UpdateNPCRank(Actor akNPC)
    ; Calculate rank based on various factors
    float influence = GetNPCInfluence(akNPC)
    float reputation = GetNPCReputation(akNPC)
    
    ; Update rank accordingly
    if influence > 0.8 && reputation > 0.8
        SetNPCRank(akNPC, "LEADER")
    elseif influence > 0.6 && reputation > 0.6
        SetNPCRank(akNPC, "ELDER")
    else
        SetNPCRank(akNPC, "MEMBER")
    endif
EndFunction

; Power dynamics
Function HandlePowerStruggles()
    Actor[] leaders = GetAllLeaders()
    
    int i = 0
    while i < leaders.Length
        Actor leader = leaders[i]
        if ShouldChallengeLeadership(leader)
            InitiatePowerStruggle(leader)
        endif
        i += 1
    endwhile
EndFunction

Function InitiatePowerStruggle(Actor akLeader)
    Actor challenger = FindStrongestChallenger(akLeader)
    if challenger
        StartPowerStruggleQuest(akLeader, challenger)
    endif
EndFunction

; Relationship management
Function UpdateRelationships()
    Actor[] npcs = Game.GetAllActors()
    
    int i = 0
    while i < npcs.Length
        Actor npc1 = npcs[i]
        
        int j = i + 1
        while j < npcs.Length
            Actor npc2 = npcs[j]
            UpdateRelationshipBetweenNPCs(npc1, npc2)
            j += 1
        endwhile
        i += 1
    endwhile
EndFunction

Function UpdateRelationshipBetweenNPCs(Actor akNPC1, Actor akNPC2)
    ; Calculate relationship factors
    float distance = GetNPCDistance(akNPC1, akNPC2)
    float interaction = GetInteractionFrequency(akNPC1, akNPC2)
    
    ; Update relationship values
    if distance < 1000.0 && interaction > 0.5
        ImproveRelationship(akNPC1, akNPC2)
    endif
EndFunction

; Utility functions
bool Function IsValidNPC(Actor akNPC)
    return akNPC && !akNPC.IsDead() && !akNPC.IsDisabled()
EndFunction

float Function GetNPCInfluence(Actor akNPC)
    ; Calculate influence based on various factors
    float baseInfluence = 0.5
    
    ; Add faction influence
    if akNPC.IsInFaction(Game.GetPlayer().GetCrimeFaction())
        baseInfluence += 0.2
    endif
    
    ; Add level-based influence
    baseInfluence += (akNPC.GetLevel() as float) / 100.0
    
    return baseInfluence
EndFunction

float Function GetNPCReputation(Actor akNPC)
    ; Calculate reputation based on actions and history
    float baseReputation = 0.5
    
    ; Add faction reputation
    if akNPC.IsInFaction(Game.GetPlayer().GetCrimeFaction())
        baseReputation += 0.3
    endif
    
    return baseReputation
EndFunction

; Debug functions
Function DebugHierarchy()
    Debug.Notification("ENA Social Hierarchy Debug:")
    Actor[] npcs = Game.GetAllActors()
    
    int i = 0
    while i < npcs.Length
        Actor npc = npcs[i]
        if IsValidNPC(npc)
            Debug.Notification(npc.GetDisplayName() + ": " + GetNPCRank(npc))
        endif
        i += 1
    endwhile
EndFunction

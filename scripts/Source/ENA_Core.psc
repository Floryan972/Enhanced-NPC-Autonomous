Scriptname ENA_Core extends Quest
{Core system for Enhanced NPC Autonomous}

; Import required game systems
import Game
import Debug
import Utility
import Actor

; Global variables
Actor[] Property NPCList Auto
GlobalVariable Property ENA_SystemEnabled Auto

; Core systems
ENA_SocialHierarchy Property SocialSystem Auto
ENA_Rituals Property RitualSystem Auto
ENA_FamilyRelations Property FamilySystem Auto
ENA_Trade Property TradeSystem Auto
ENA_Migration Property MigrationSystem Auto

; Events
Event OnInit()
    InitializeSystems()
    RegisterForUpdate(5.0) ; Update every 5 seconds
EndEvent

Event OnUpdate()
    if !ENA_SystemEnabled.GetValue()
        return
    endif
    
    UpdateSystems()
EndEvent

; Core functions
Function InitializeSystems()
    Debug.Notification("ENA: Initializing systems...")
    
    ; Initialize all subsystems
    SocialSystem.Initialize()
    RitualSystem.Initialize()
    FamilySystem.Initialize()
    TradeSystem.Initialize()
    MigrationSystem.Initialize()
    
    Debug.Notification("ENA: Systems initialized")
EndFunction

Function UpdateSystems()
    ; Update each system
    SocialSystem.Update()
    RitualSystem.Update()
    FamilySystem.Update()
    TradeSystem.Update()
    MigrationSystem.Update()
    
    ; Handle cross-system interactions
    HandleSystemInteractions()
EndFunction

Function HandleSystemInteractions()
    ; Handle interactions between different systems
    HandleSocialTradeInteractions()
    HandleFamilyMigrationInteractions()
    HandleRitualSeasonalEvents()
EndFunction

; Utility functions
Function RegisterNPC(Actor akNPC)
    if !NPCList
        NPCList = new Actor[0]
    endif
    
    NPCList.Add(akNPC)
    InitializeNPCData(akNPC)
EndFunction

Function InitializeNPCData(Actor akNPC)
    ; Initialize NPC data in all systems
    SocialSystem.InitializeNPC(akNPC)
    FamilySystem.InitializeNPC(akNPC)
    TradeSystem.InitializeNPC(akNPC)
EndFunction

; Debug functions
Function DebugMode(bool enable)
    Debug.Notification("ENA Debug Mode: " + enable)
    ; Enable detailed logging and monitoring
EndFunction

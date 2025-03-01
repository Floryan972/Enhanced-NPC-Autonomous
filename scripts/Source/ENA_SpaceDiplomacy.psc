Scriptname ENA_SpaceDiplomacy extends Quest
{Handles interstellar diplomacy and faction relations}

; Import required game systems
import Game
import Debug
import Utility
import Location

; Enums and Structs
Struct DiplomaticRelation
    Faction faction1
    Faction faction2
    float relation ; -1.0 to 1.0
    String status ; PEACE, WAR, ALLIANCE, TRADE_AGREEMENT
    float tradeBonus
    bool hasEmbassy
EndStruct

Struct DiplomaticEvent
    String type
    Faction initiator
    Faction target
    float importance
    String[] conditions
    Form[] rewards
    bool isActive
EndStruct

Struct Embassy
    Location location
    Faction owner
    Faction host
    ActorBase[] diplomats
    bool isActive
EndStruct

; Properties
DiplomaticRelation[] Property Relations Auto
DiplomaticEvent[] Property ActiveEvents Auto
Embassy[] Property Embassies Auto
float Property UpdateInterval = 12.0 Auto

; Events
Event OnInit()
    Initialize()
    RegisterForUpdateGameTime(UpdateInterval)
EndEvent

Event OnUpdateGameTime()
    UpdateDiplomacy()
EndEvent

; Core functions
Function Initialize()
    InitializeRelations()
    SetupEmbassies()
    StartInitialEvents()
EndFunction

Function InitializeRelations()
    ; Get all major factions
    Faction[] factions = GetAllMajorFactions()
    
    ; Setup initial relations
    int i = 0
    while i < factions.Length
        Faction faction1 = factions[i]
        
        int j = i + 1
        while j < factions.Length
            Faction faction2 = factions[j]
            
            DiplomaticRelation relation = CreateRelation(faction1, faction2)
            Relations.Add(relation)
            
            j += 1
        endwhile
        i += 1
    endwhile
EndFunction

Function SetupEmbassies()
    ; Setup embassies in major systems
    Location[] capitals = GetFactionCapitals()
    
    int i = 0
    while i < capitals.Length
        Location capital = capitals[i]
        Faction host = GetSystemFaction(capital)
        
        ; Create embassies for allied factions
        Faction[] allies = GetAlliedFactions(host)
        int j = 0
        while j < allies.Length
            CreateEmbassy(capital, host, allies[j])
            j += 1
        endwhile
        
        i += 1
    endwhile
EndFunction

; Diplomatic relations
Function UpdateRelations()
    int i = 0
    while i < Relations.Length
        DiplomaticRelation relation = Relations[i]
        
        ; Update based on recent events
        UpdateRelationFromEvents(relation)
        
        ; Check for status changes
        CheckRelationStatus(relation)
        
        ; Update trade bonuses
        UpdateTradeBonus(relation)
        
        i += 1
    endwhile
EndFunction

Function UpdateRelationFromEvents(DiplomaticRelation relation)
    ; Get recent events between factions
    DiplomaticEvent[] events = GetRecentEvents(relation.faction1, relation.faction2)
    
    int i = 0
    while i < events.Length
        DiplomaticEvent event = events[i]
        
        ; Impact on relations
        float impact = CalculateEventImpact(event)
        relation.relation += impact
        
        ; Clamp relation value
        relation.relation = Math.Clamp(relation.relation, -1.0, 1.0)
        
        i += 1
    endwhile
EndFunction

Function CheckRelationStatus(DiplomaticRelation relation)
    ; Update diplomatic status based on relation value
    if relation.relation >= 0.8
        relation.status = "ALLIANCE"
        HandleNewAlliance(relation)
    elseif relation.relation <= -0.8
        relation.status = "WAR"
        HandleWarDeclaration(relation)
    elseif relation.relation >= 0.3
        relation.status = "TRADE_AGREEMENT"
        HandleTradeAgreement(relation)
    else
        relation.status = "PEACE"
    endif
EndFunction

; Embassy management
Function CreateEmbassy(Location capital, Faction host, Faction owner)
    Embassy embassy = new Embassy
    embassy.location = capital
    embassy.host = host
    embassy.owner = owner
    embassy.isActive = true
    
    ; Create embassy building
    PlaceEmbassyBuilding(embassy)
    
    ; Assign diplomats
    embassy.diplomats = CreateDiplomats(owner)
    
    Embassies.Add(embassy)
EndFunction

Function UpdateEmbassies()
    int i = 0
    while i < Embassies.Length
        Embassy embassy = Embassies[i]
        if embassy.isActive
            UpdateEmbassyStaff(embassy)
            HandleDiplomaticMeetings(embassy)
            UpdateEmbassyStatus(embassy)
        endif
        i += 1
    endwhile
EndFunction

; Diplomatic events
Function StartDiplomaticEvent(String eventType, Faction initiator, Faction target)
    DiplomaticEvent newEvent = new DiplomaticEvent
    newEvent.type = eventType
    newEvent.initiator = initiator
    newEvent.target = target
    newEvent.isActive = true
    
    ; Configure based on type
    if eventType == "PEACE_TALKS"
        SetupPeaceTalks(newEvent)
    elseif eventType == "TRADE_NEGOTIATION"
        SetupTradeNegotiation(newEvent)
    elseif eventType == "ALLIANCE_PROPOSAL"
        SetupAllianceProposal(newEvent)
    endif
    
    ActiveEvents.Add(newEvent)
EndFunction

Function UpdateEvents()
    int i = 0
    while i < ActiveEvents.Length
        DiplomaticEvent event = ActiveEvents[i]
        
        if event.isActive
            UpdateEventProgress(event)
            CheckEventConditions(event)
            
            if IsEventComplete(event)
                CompleteEvent(event)
                ActiveEvents.Remove(i)
            else
                i += 1
            endif
        endif
    endwhile
EndFunction

; War and peace
Function HandleWarDeclaration(DiplomaticRelation relation)
    Debug.Notification(relation.faction1.GetName() + " and " + relation.faction2.GetName() + " are now at war!")
    
    ; Close embassies
    CloseEmbassies(relation.faction1, relation.faction2)
    
    ; Cancel trade agreements
    CancelTradeAgreements(relation)
    
    ; Start military activities
    StartMilitaryOperations(relation)
EndFunction

Function HandlePeaceProcess(DiplomaticRelation relation)
    ; Start peace talks
    StartDiplomaticEvent("PEACE_TALKS", relation.faction1, relation.faction2)
    
    ; Cease military operations
    CeaseMilitaryOperations(relation)
    
    ; Prepare peace terms
    PreparePeaceTerms(relation)
EndFunction

; Trade and economic relations
Function UpdateTradeBonus(DiplomaticRelation relation)
    float baseBonus = 0.1 ; 10% base bonus
    
    ; Modify based on relation
    if relation.status == "ALLIANCE"
        baseBonus *= 2.0
    elseif relation.status == "TRADE_AGREEMENT"
        baseBonus *= 1.5
    endif
    
    ; Add embassy bonus
    if relation.hasEmbassy
        baseBonus *= 1.2
    endif
    
    relation.tradeBonus = baseBonus
EndFunction

Function HandleTradeAgreement(DiplomaticRelation relation)
    if relation.status != "TRADE_AGREEMENT"
        Debug.Notification("New trade agreement between " + relation.faction1.GetName() + " and " + relation.faction2.GetName())
        
        ; Setup trade routes
        ENA_SpaceTrade.getInstance().CreateTradeRoute(
            GetFactionHomeSystem(relation.faction1),
            GetFactionHomeSystem(relation.faction2)
        )
        
        ; Update relation status
        relation.status = "TRADE_AGREEMENT"
        relation.tradeBonus = 0.15 ; 15% trade bonus
    endif
EndFunction

; Utility functions
bool Function AreFactionsFriendly(Faction faction1, Faction faction2)
    DiplomaticRelation relation = GetRelation(faction1, faction2)
    return relation && relation.relation > 0
EndFunction

DiplomaticRelation Function GetRelation(Faction faction1, Faction faction2)
    int i = 0
    while i < Relations.Length
        DiplomaticRelation relation = Relations[i]
        if (relation.faction1 == faction1 && relation.faction2 == faction2) || \
           (relation.faction1 == faction2 && relation.faction2 == faction1)
            return relation
        endif
        i += 1
    endwhile
    return None
EndFunction

Function UpdateDiplomacy()
    UpdateRelations()
    UpdateEmbassies()
    UpdateEvents()
    
    ; Handle special events
    CheckForWarDeclarations()
    CheckForPeaceOffers()
    UpdateTradeAgreements()
EndFunction

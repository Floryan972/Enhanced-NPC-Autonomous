Scriptname ENA_SpaceMigration extends Quest
{Handles interplanetary migration and colony management}

; Import required game systems
import Game
import Debug
import Utility
import SpaceshipReference
import Location

; Enums and Structs
Struct Colony
    String name
    Location planet
    float population
    float resources
    float happiness
    float stability
    ActorBase[] settlers
    Form[] buildings
    bool isActive
EndStruct

Struct MigrationGroup
    ActorBase[] members
    Colony origin
    Colony destination
    SpaceshipReference transport
    float progress
    bool isEmergency
EndStruct

; Properties
Colony[] Property ActiveColonies Auto
MigrationGroup[] Property ActiveMigrations Auto
float Property UpdateInterval = 10.0 Auto

; Events
Event OnInit()
    Initialize()
    RegisterForUpdateGameTime(UpdateInterval)
EndEvent

Event OnUpdateGameTime()
    UpdateMigration()
EndEvent

; Core functions
Function Initialize()
    InitializeColonies()
    SetupMigrationRoutes()
EndFunction

Function InitializeColonies()
    ; Find all player-owned or NPC colonies
    Location[] planets = Game.GetAllDiscoveredLocations()
    
    int i = 0
    while i < planets.Length
        Location planet = planets[i]
        if IsValidColonyLocation(planet)
            Colony colony = CreateColony(planet)
            if colony
                ActiveColonies.Add(colony)
            endif
        endif
        i += 1
    endwhile
EndFunction

Function SetupMigrationRoutes()
    ; Setup migration paths between colonies
    int i = 0
    while i < ActiveColonies.Length
        Colony colony1 = ActiveColonies[i]
        
        int j = i + 1
        while j < ActiveColonies.Length
            Colony colony2 = ActiveColonies[j]
            
            if ShouldCreateMigrationRoute(colony1, colony2)
                SetupMigrationRoute(colony1, colony2)
            endif
            j += 1
        endwhile
        i += 1
    endwhile
EndFunction

; Colony management
Colony Function CreateColony(Location planet)
    Colony colony = new Colony
    colony.name = planet.GetName()
    colony.planet = planet
    colony.isActive = true
    
    ; Initialize colony properties
    colony.population = CalculateInitialPopulation(planet)
    colony.resources = CalculateInitialResources(planet)
    colony.happiness = 0.7 ; Base happiness
    colony.stability = 1.0 ; Full stability
    
    ; Setup initial buildings and settlers
    colony.buildings = GetInitialBuildings(planet)
    colony.settlers = GetInitialSettlers(planet)
    
    return colony
EndFunction

Function UpdateColony(Colony colony)
    if !colony.isActive
        return
    endif
    
    ; Update population
    UpdatePopulation(colony)
    
    ; Update resources
    UpdateResources(colony)
    
    ; Update happiness and stability
    UpdateHappiness(colony)
    UpdateStability(colony)
    
    ; Check for emergency situations
    CheckEmergencyConditions(colony)
    
    ; Update buildings and infrastructure
    UpdateBuildings(colony)
EndFunction

; Migration management
Function StartMigration(Colony origin, Colony destination, int populationCount)
    if !CanMigrate(origin, destination)
        Debug.Notification("Migration conditions not met")
        return
    endif
    
    MigrationGroup migration = new MigrationGroup
    migration.origin = origin
    migration.destination = destination
    
    ; Select migrants
    migration.members = SelectMigrants(origin, populationCount)
    
    ; Assign transport
    migration.transport = RequestTransportShip(origin, destination)
    
    if migration.transport
        ActiveMigrations.Add(migration)
        NotifyMigrationStart(migration)
    endif
EndFunction

Function UpdateMigration()
    int i = 0
    while i < ActiveMigrations.Length
        MigrationGroup migration = ActiveMigrations[i]
        
        if migration.transport
            UpdateMigrationProgress(migration)
            
            if IsMigrationComplete(migration)
                CompleteMigration(migration)
                ActiveMigrations.Remove(i)
            else
                i += 1
            endif
        else
            ; Transport lost/destroyed
            HandleFailedMigration(migration)
            ActiveMigrations.Remove(i)
        endif
    endwhile
    
    ; Update all colonies
    UpdateAllColonies()
EndFunction

; Population management
Function UpdatePopulation(Colony colony)
    float growthRate = CalculateGrowthRate(colony)
    float deathRate = CalculateDeathRate(colony)
    
    ; Apply population changes
    float populationChange = (growthRate - deathRate) * colony.population
    colony.population += populationChange
    
    ; Update settler list
    if populationChange > 0
        AddNewSettlers(colony, populationChange as int)
    elseif populationChange < 0
        RemoveSettlers(colony, (-populationChange) as int)
    endif
EndFunction

Function AddNewSettlers(Colony colony, int count)
    int i = 0
    while i < count
        ActorBase settler = CreateNewSettler(colony)
        if settler
            colony.settlers.Add(settler)
        endif
        i += 1
    endwhile
EndFunction

; Resource management
Function UpdateResources(Colony colony)
    ; Production
    float production = CalculateResourceProduction(colony)
    
    ; Consumption
    float consumption = CalculateResourceConsumption(colony)
    
    ; Trade impact
    float tradeBalance = CalculateTradeBalance(colony)
    
    ; Update resources
    colony.resources += production - consumption + tradeBalance
    
    ; Handle resource shortages
    if colony.resources < GetMinimumResources(colony)
        HandleResourceShortage(colony)
    endif
EndFunction

; Emergency handling
Function CheckEmergencyConditions(Colony colony)
    if colony.resources < GetCriticalResourceLevel(colony)
        InitiateEmergencyProtocol(colony, "RESOURCE_CRISIS")
    endif
    
    if colony.stability < 0.3
        InitiateEmergencyProtocol(colony, "STABILITY_CRISIS")
    endif
    
    if colony.happiness < 0.2
        InitiateEmergencyProtocol(colony, "HAPPINESS_CRISIS")
    endif
EndFunction

Function InitiateEmergencyProtocol(Colony colony, String crisisType)
    Debug.Notification("Emergency in " + colony.name + ": " + crisisType)
    
    if crisisType == "RESOURCE_CRISIS"
        ; Start emergency resource migration
        Colony nearestStableColony = FindNearestStableColony(colony)
        if nearestStableColony
            StartEmergencyResourceTransfer(nearestStableColony, colony)
        endif
    elseif crisisType == "STABILITY_CRISIS"
        ; Deploy security forces
        DeploySecurityForces(colony)
    elseif crisisType == "HAPPINESS_CRISIS"
        ; Implement emergency morale measures
        ImplementMoraleMeasures(colony)
    endif
EndFunction

; Utility functions
bool Function IsValidColonyLocation(Location planet)
    return planet && planet.HasKeyword(Game.GetForm("ColonizablePlanetKeyword") as Keyword)
EndFunction

float Function CalculateGrowthRate(Colony colony)
    float baseRate = 0.01 ; 1% base growth
    
    ; Modify based on conditions
    if colony.happiness > 0.8
        baseRate *= 1.5
    endif
    
    if colony.resources > GetOptimalResources(colony)
        baseRate *= 1.3
    endif
    
    return baseRate
EndFunction

float Function CalculateDeathRate(Colony colony)
    float baseRate = 0.005 ; 0.5% base death rate
    
    ; Modify based on conditions
    if colony.resources < GetMinimumResources(colony)
        baseRate *= 2.0
    endif
    
    if colony.stability < 0.5
        baseRate *= 1.5
    endif
    
    return baseRate
EndFunction

ActorBase Function CreateNewSettler(Colony colony)
    ; Create a new settler based on colony type
    Form settlerBase = Game.GetForm(0x00000F98) ; Base settler form
    return colony.planet.PlaceActorAtMe(settlerBase) as ActorBase
EndFunction

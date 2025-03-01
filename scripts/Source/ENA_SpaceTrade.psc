Scriptname ENA_SpaceTrade extends Quest
{Handles interplanetary trade and resource management}

; Import required game systems
import Game
import Debug
import Utility
import SpaceshipReference

; Enums and Structs
Struct TradeRoute
    Location startSystem
    Location endSystem
    float distance
    float risk
    Form[] resources
    SpaceshipReference[] activeShips
    bool isActive
EndStruct

Struct SpaceResource
    String name
    Form baseItem
    int quantity
    float value
    Location origin
    bool isRare
    bool isIllegal
EndStruct

; Properties
TradeRoute[] Property ActiveRoutes Auto
Location[] Property TradingSystems Auto
float Property UpdateInterval = 5.0 Auto

; Events
Event OnInit()
    Initialize()
    RegisterForUpdateGameTime(UpdateInterval)
EndEvent

Event OnUpdateGameTime()
    UpdateTrade()
EndEvent

; Core functions
Function Initialize()
    InitializeTradeSystems()
    SetupInitialRoutes()
EndFunction

Function InitializeTradeSystems()
    ; Get all discovered star systems
    Location[] systems = Game.GetAllDiscoveredLocations()
    
    int i = 0
    while i < systems.Length
        Location system = systems[i]
        if IsValidTradeSystem(system)
            TradingSystems.Add(system)
            SetupSystemResources(system)
        endif
        i += 1
    endwhile
EndFunction

Function SetupInitialRoutes()
    ; Create initial trade routes between major systems
    int i = 0
    while i < TradingSystems.Length
        Location system1 = TradingSystems[i]
        
        int j = i + 1
        while j < TradingSystems.Length
            Location system2 = TradingSystems[j]
            
            if ShouldCreateRoute(system1, system2)
                CreateTradeRoute(system1, system2)
            endif
            j += 1
        endwhile
        i += 1
    endwhile
EndFunction

; Trade route management
Function CreateTradeRoute(Location startSystem, Location endSystem)
    TradeRoute route = new TradeRoute
    route.startSystem = startSystem
    route.endSystem = endSystem
    route.isActive = true
    
    ; Calculate route properties
    route.distance = CalculateSystemDistance(startSystem, endSystem)
    route.risk = CalculateRouteRisk(startSystem, endSystem)
    
    ; Assign resources
    route.resources = GetTradeableResources(startSystem, endSystem)
    
    ; Initialize ships
    route.activeShips = AssignTradeShips(route)
    
    ActiveRoutes.Add(route)
EndFunction

Function UpdateTrade()
    int i = 0
    while i < ActiveRoutes.Length
        TradeRoute route = ActiveRoutes[i]
        if route.isActive
            UpdateTradeRoute(route)
            UpdateShipPositions(route)
            HandleTradeEvents(route)
        endif
        i += 1
    endwhile
    
    UpdateResourcePrices()
    HandlePirateActivity()
EndFunction

; Ship management
SpaceshipReference[] Function AssignTradeShips(TradeRoute route)
    SpaceshipReference[] ships = new SpaceshipReference[0]
    
    ; Calculate needed ships based on route distance and resources
    int neededShips = Math.Ceiling(route.distance / 1000.0) as int
    neededShips = Math.Max(neededShips, 1)
    
    ; Create or assign ships
    int i = 0
    while i < neededShips
        SpaceshipReference ship = CreateTradeShip(route)
        if ship
            ships.Add(ship)
        endif
        i += 1
    endwhile
    
    return ships
EndFunction

SpaceshipReference Function CreateTradeShip(TradeRoute route)
    ; Create a new trade ship
    Form shipBase = Game.GetForm(0x00000F99) ; Trade ship base form
    SpaceshipReference newShip = route.startSystem.PlaceShipAtMe(shipBase) as SpaceshipReference
    
    if newShip
        ; Configure ship
        newShip.SetValue(Game.GetForm("TradeShipAV") as ActorValue, 1.0)
        newShip.AddToFaction(Game.GetForm("TraderFaction") as Faction)
        
        ; Add crew
        AddTradeCrewToShip(newShip)
    endif
    
    return newShip
EndFunction

Function UpdateShipPositions(TradeRoute route)
    int i = 0
    while i < route.activeShips.Length
        SpaceshipReference ship = route.activeShips[i]
        if ship
            ; Update ship position along trade route
            float progress = GetShipProgress(ship)
            Vector3 newPosition = CalculateRoutePosition(route, progress)
            
            ; Move ship
            ship.MoveTo(Game.GetForm(newPosition))
            
            ; Handle docking and trading
            if IsAtTradeStation(ship)
                HandleTradeTransaction(ship, route)
            endif
        endif
        i += 1
    endwhile
EndFunction

; Resource management
Function SetupSystemResources(Location system)
    ; Get system type
    String systemType = GetSystemType(system)
    
    ; Add resources based on system type
    if systemType == "INDUSTRIAL"
        AddSystemResource(system, "MATERIALS", 1000)
        AddSystemResource(system, "TECHNOLOGY", 500)
    elseif systemType == "AGRICULTURAL"
        AddSystemResource(system, "FOOD", 1500)
        AddSystemResource(system, "ORGANIC", 800)
    elseif systemType == "MINING"
        AddSystemResource(system, "MINERALS", 2000)
        AddSystemResource(system, "RARE_ELEMENTS", 300)
    endif
EndFunction

Function UpdateResourcePrices()
    Location[] systems = TradingSystems
    int i = 0
    while i < systems.Length
        Location system = systems[i]
        
        ; Update prices based on supply and demand
        SpaceResource[] resources = GetSystemResources(system)
        int j = 0
        while j < resources.Length
            SpaceResource resource = resources[j]
            
            ; Calculate new value
            float supplyFactor = GetResourceSupply(resource, system)
            float demandFactor = GetResourceDemand(resource, system)
            
            resource.value = resource.value * (demandFactor / supplyFactor)
            
            ; Update rarity status
            resource.isRare = (resource.quantity < 100)
            
            j += 1
        endwhile
        
        i += 1
    endwhile
EndFunction

; Event handlers
Function HandleTradeEvents(TradeRoute route)
    ; Handle random events
    if Utility.RandomFloat(0.0, 1.0) < route.risk
        HandlePirateAttack(route)
    endif
    
    ; Handle resource shortages
    CheckResourceShortages(route)
    
    ; Handle diplomatic events
    UpdateSystemRelations(route)
EndFunction

Function HandlePirateAttack(TradeRoute route)
    ; Select random ship from route
    int shipIndex = Utility.RandomInt(0, route.activeShips.Length - 1)
    SpaceshipReference targetShip = route.activeShips[shipIndex]
    
    if targetShip
        ; Spawn pirate ships
        int pirateCount = Utility.RandomInt(1, 3)
        SpaceshipReference[] pirates = SpawnPirateShips(targetShip, pirateCount)
        
        ; Start combat
        StartPirateCombat(targetShip, pirates)
        
        ; Update route risk
        route.risk = Math.Min(route.risk + 0.1, 1.0)
    endif
EndFunction

; Utility functions
bool Function IsValidTradeSystem(Location system)
    return system && system.HasKeyword(Game.GetForm("TradeSystemKeyword") as Keyword)
EndFunction

float Function CalculateSystemDistance(Location system1, Location2)
    ; Calculate actual distance between star systems
    Vector3 pos1 = GetSystemPosition(system1)
    Vector3 pos2 = GetSystemPosition(system2)
    
    return Math.Sqrt(
        Math.Pow(pos2.x - pos1.x, 2) +
        Math.Pow(pos2.y - pos1.y, 2) +
        Math.Pow(pos2.z - pos1.z, 2)
    )
EndFunction

float Function CalculateRouteRisk(Location system1, Location system2)
    float baseRisk = 0.1
    
    ; Add distance factor
    float distance = CalculateSystemDistance(system1, system2)
    baseRisk += distance / 10000.0
    
    ; Add pirate activity factor
    baseRisk += GetPirateActivity(system1) * 0.2
    baseRisk += GetPirateActivity(system2) * 0.2
    
    ; Add political factor
    if !AreSystemsAllied(system1, system2)
        baseRisk += 0.3
    endif
    
    return Math.Min(baseRisk, 1.0)
EndFunction

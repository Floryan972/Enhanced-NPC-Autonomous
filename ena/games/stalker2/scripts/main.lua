--[[
Script principal d'intégration ENA pour STALKER 2
]]

local ENA = {}

-- Configuration
ENA.config = {
    enabled = true,
    debug = false,
    update_rate = 0.1
}

-- Chemins d'intégration
ENA.paths = {
    scripts = "gamedata/scripts/ena",
    configs = "gamedata/configs/ena",
    ai = "gamedata/ai/ena"
}

-- Initialisation
function ENA:Initialize()
    self:LoadManagers()
    self:LoadBehaviors()
    self:LoadEvents()
    self:SetupHooks()
end

-- Chargement des gestionnaires
function ENA:LoadManagers()
    self.ai_manager = require("ena.managers.ai_manager")
    self.world_manager = require("ena.managers.world_manager")
    self.quest_manager = require("ena.managers.quest_manager")
    self.faction_manager = require("ena.managers.faction_manager")
end

-- Chargement des comportements
function ENA:LoadBehaviors()
    self.mutant_behavior = require("ena.behaviors.mutant_behavior")
    self.stalker_behavior = require("ena.behaviors.stalker_behavior")
    self.anomaly_behavior = require("ena.behaviors.anomaly_behavior")
end

-- Chargement des événements
function ENA:LoadEvents()
    self.emission_event = require("ena.events.emission_event")
    self.faction_war_event = require("ena.events.faction_war_event")
    self.mutant_migration_event = require("ena.events.mutant_migration_event")
end

-- Configuration des hooks du jeu
function ENA:SetupHooks()
    -- Hook de mise à jour
    self:HookUpdateLoop()
    
    -- Hooks d'événements
    self:HookGameEvents()
    
    -- Hooks de quêtes
    self:HookQuestSystem()
end

-- Hook de la boucle de mise à jour
function ENA:HookUpdateLoop()
    local last_update = 0
    
    function on_update()
        local current_time = time_global()
        if current_time - last_update >= self.config.update_rate then
            self:Update()
            last_update = current_time
        end
    end
    
    register_callback("on_update", on_update)
end

-- Hook des événements du jeu
function ENA:HookGameEvents()
    function on_game_start()
        self:Initialize()
    end
    
    function on_game_load()
        self:LoadState()
    end
    
    function on_game_save()
        self:SaveState()
    end
    
    register_callback("on_game_start", on_game_start)
    register_callback("on_game_load", on_game_load)
    register_callback("on_game_save", on_game_save)
end

-- Hook du système de quêtes
function ENA:HookQuestSystem()
    function on_quest_update(quest_id)
        self.quest_manager:OnQuestUpdate(quest_id)
    end
    
    function on_quest_complete(quest_id)
        self.quest_manager:OnQuestComplete(quest_id)
    end
    
    register_callback("on_quest_update", on_quest_update)
    register_callback("on_quest_complete", on_quest_complete)
end

-- Mise à jour principale
function ENA:Update()
    if not self.config.enabled then return end
    
    -- Mise à jour des gestionnaires
    self.ai_manager:Update()
    self.world_manager:Update()
    self.quest_manager:Update()
    self.faction_manager:Update()
    
    -- Mise à jour des comportements
    self.mutant_behavior:Update()
    self.stalker_behavior:Update()
    self.anomaly_behavior:Update()
    
    -- Mise à jour des événements
    self.emission_event:Update()
    self.faction_war_event:Update()
    self.mutant_migration_event:Update()
end

-- Sauvegarde de l'état
function ENA:SaveState()
    local state = {
        ai = self.ai_manager:GetState(),
        world = self.world_manager:GetState(),
        quests = self.quest_manager:GetState(),
        factions = self.faction_manager:GetState()
    }
    
    utils.save_state("ena_state", state)
end

-- Chargement de l'état
function ENA:LoadState()
    local state = utils.load_state("ena_state")
    if state then
        self.ai_manager:SetState(state.ai)
        self.world_manager:SetState(state.world)
        self.quest_manager:SetState(state.quests)
        self.faction_manager:SetState(state.factions)
    end
end

return ENA

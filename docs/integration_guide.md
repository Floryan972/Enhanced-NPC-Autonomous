# Guide d'Intégration ENA

## Table des Matières
1. [STALKER 2](#stalker-2)
2. [Cyberpunk 2077](#cyberpunk-2077)
3. [Starfield](#starfield)
4. [Red Dead Redemption 2](#red-dead-redemption-2)

## STALKER 2

### Installation
1. Copier le dossier `ena/games/stalker2` dans `gamedata/scripts/ena`
2. Ajouter dans `gamedata/scripts/ena_loader.script`:
```lua
function on_game_start()
    -- Chargement du système ENA
    local ena = require("ena.main")
    ena:Initialize()
end
```

### Structure des Fichiers
```
gamedata/
├── scripts/
│   ├── ena/
│   │   ├── main.lua
│   │   ├── behaviors/
│   │   └── systems/
├── configs/
│   └── ena/
└── ai/
    └── ena/
```

### Intégration des Comportements
```lua
-- Exemple d'intégration d'un stalker
function create_stalker()
    local npc_data = {
        role = "stalker",
        faction = "loners",
        behaviors = {
            "anomaly_awareness",
            "artifact_hunting",
            "combat"
        }
    }
    
    ena.ai_manager:register_npc("stalker_001", npc_data)
end
```

## Cyberpunk 2077

### Installation
1. Copier le dossier `ena/games/cyberpunk2077` dans `r6/scripts/ena`
2. Ajouter dans `r6/scripts/ena_loader.reds`:
```swift
module ENALoader {
    public class ENASystem {
        private let system: ref<ENAMain>;
        
        public func Initialize() {
            this.system = new ENAMain();
            this.system.Initialize();
        }
    }
}
```

### Structure des Fichiers
```
r6/
├── scripts/
│   ├── ena/
│   │   ├── main.reds
│   │   ├── behaviors/
│   │   └── systems/
├── tweaks/
│   └── ena/
└── config/
    └── ena/
```

### Intégration des Comportements
```swift
// Exemple d'intégration d'un netrunner
public func CreateNetrunner() {
    let npcData: ref<NPCData> = new NPCData();
    npcData.role = "netrunner";
    npcData.faction = "voodoo_boys";
    npcData.behaviors = [
        "hacking",
        "stealth",
        "combat"
    ];
    
    this.system.aiManager.RegisterNPC("netrunner_001", npcData);
}
```

## Starfield

### Installation
1. Copier le dossier `ena/games/starfield` dans `Data/Scripts/Source/ena`
2. Ajouter dans `Data/Scripts/Source/ena_loader.psc`:
```papyrus
ScriptName ENALoader extends Quest

Event OnInit()
    ; Chargement du système ENA
    ENASystem.Initialize()
EndEvent
```

### Structure des Fichiers
```
Data/
├── Scripts/
│   └── Source/
│       ├── ena/
│       │   ├── main.psc
│       │   ├── behaviors/
│       │   └── systems/
└── ena/
    └── config/
```

### Intégration des Comportements
```papyrus
; Exemple d'intégration d'un marchand spatial
Function CreateSpaceTrader()
    Actor npcRef = Game.GetForm(0x00000123) as Actor
    
    ENASystem.RegisterNPC(npcRef, {
        "role": "trader",
        "faction": "constellation",
        "behaviors": [
            "trading",
            "space_navigation",
            "combat"
        ]
    })
EndFunction
```

## Red Dead Redemption 2

### Installation
1. Copier le dossier `ena/games/rdr2` dans `scripts/ena`
2. Ajouter dans `scripts/ena_loader.lua`:
```lua
function InitializeENA()
    local ena = require("ena.main")
    ena:Initialize()
end

addEventHandler("onResourceStart", resourceRoot, InitializeENA)
```

### Structure des Fichiers
```
scripts/
├── ena/
│   ├── main.lua
│   ├── behaviors/
│   └── systems/
└── config/
    └── ena/
```

### Intégration des Comportements
```lua
-- Exemple d'intégration d'un hors-la-loi
function create_outlaw()
    local npc_data = {
        role = "outlaw",
        faction = "vanderlinde",
        behaviors = {
            "robbery",
            "horseback",
            "combat"
        }
    }
    
    ena.ai_manager:register_npc("outlaw_001", npc_data)
end
```

## Configuration Avancée

### Système de Comportements
```json
{
    "behaviors": {
        "combat": {
            "priority": 1.0,
            "conditions": ["threat_detected"],
            "actions": ["engage", "take_cover"]
        },
        "social": {
            "priority": 0.8,
            "conditions": ["friendly_npc_nearby"],
            "actions": ["greet", "chat"]
        }
    }
}
```

### Système d'Événements
```json
{
    "events": {
        "faction_war": {
            "probability": 0.1,
            "min_duration": 1800,
            "max_duration": 3600,
            "participants": {
                "min": 2,
                "max": 4
            }
        }
    }
}
```

### Système de Ressources
```json
{
    "resources": {
        "ammo": {
            "max": 100,
            "regen_rate": 0.1
        },
        "health": {
            "max": 100,
            "regen_rate": 0.05
        }
    }
}
```

## Débogage

### Logs
```json
{
    "logging": {
        "level": "DEBUG",
        "file": "logs/ena.log",
        "console": true
    }
}
```

### Console de Débogage
Chaque jeu a sa propre console de débogage accessible via :
- STALKER 2: `ena_debug` dans la console
- Cyberpunk 2077: `ENADebug.Toggle()`
- Starfield: `ENA.ShowDebug` dans la console
- RDR2: `ena.debug()` dans la console

### Commandes Utiles
```
ena.list_npcs()        # Liste tous les PNJ
ena.show_behaviors()    # Affiche les comportements actifs
ena.show_events()      # Affiche les événements en cours
ena.reload_config()    # Recharge la configuration
```

## Résolution des Problèmes

### Problèmes Courants
1. **Les PNJ ne réagissent pas**
   - Vérifier que l'initialisation est correcte
   - Vérifier les logs pour les erreurs
   - S'assurer que les comportements sont enregistrés

2. **Performances faibles**
   - Réduire `max_npcs` dans la configuration
   - Augmenter `update_rate`
   - Désactiver le débogage

3. **Erreurs de script**
   - Vérifier la compatibilité des versions
   - Mettre à jour les dépendances
   - Consulter les logs d'erreur

## Support

### Ressources
- Documentation API : `docs/api.md`
- Exemples : `examples/`
- Wiki : https://github.com/votre-repo/ena/wiki

### Contact
- Discord : [Lien Discord]
- Email : support@ena-system.com
- GitHub Issues : [Lien Issues]

# Guide d'Installation ENA avec Vortex Mod Manager

## Structure des Archives pour Vortex

### STALKER 2
```
fomod/
├── info.xml
└── ModuleConfig.xml
gamedata/
├── scripts/
│   ├── ena/
│   │   ├── main.lua
│   │   ├── behaviors/
│   │   └── systems/
├── configs/
│   └── ena/
└── meta.ini
```

### Cyberpunk 2077
```
fomod/
├── info.xml
└── ModuleConfig.xml
r6/
├── scripts/
│   ├── ena/
│   │   ├── main.reds
│   │   ├── behaviors/
│   │   └── systems/
├── tweaks/
│   └── ena/
└── archive/
    └── pc/
        └── mod/
            └── ena.archive
```

### Starfield
```
fomod/
├── info.xml
└── ModuleConfig.xml
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

## Configuration FOMOD

### info.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<fomod>
    <Name>Enhanced NPC Autonomous (ENA)</Name>
    <Author>ENA Team</Author>
    <Version>1.0.0</Version>
    <Website>https://www.ena-system.com</Website>
    <Description>Système avancé d'IA pour les PNJ</Description>
    <Groups>
        <element>Gameplay</element>
        <element>AI</element>
    </Groups>
</fomod>
```

### ModuleConfig.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <moduleName>Enhanced NPC Autonomous (ENA)</moduleName>
    <installSteps order="Explicit">
        <installStep name="Configuration">
            <optionalFileGroups order="Explicit">
                <group name="Core" type="SelectExactlyOne">
                    <plugins order="Explicit">
                        <plugin name="Standard">
                            <description>Installation standard</description>
                            <files>
                                <folder source="gamedata" destination="" />
                            </files>
                            <typeDescriptor>
                                <type name="Required"/>
                            </typeDescriptor>
                        </plugin>
                    </plugins>
                </group>
                <group name="Options" type="SelectAny">
                    <plugins order="Explicit">
                        <plugin name="Debug Tools">
                            <description>Outils de débogage</description>
                            <files>
                                <folder source="debug" destination="" />
                            </files>
                        </plugin>
                        <plugin name="Enhanced Behaviors">
                            <description>Comportements avancés</description>
                            <files>
                                <folder source="enhanced" destination="" />
                            </files>
                        </plugin>
                    </plugins>
                </group>
            </optionalFileGroups>
        </installStep>
    </installSteps>
</config>
```

## Instructions d'Installation

### 1. Préparation
1. Télécharger la dernière version d'ENA pour votre jeu
2. Vérifier que le fichier est au format `.7z` ou `.zip`
3. S'assurer que Vortex est configuré pour votre jeu

### 2. Installation via Vortex
1. Ouvrir Vortex
2. Cliquer sur "Installer depuis un fichier"
3. Sélectionner l'archive ENA
4. Dans l'assistant d'installation :
   - Choisir "Installation standard"
   - Sélectionner les options désirées
5. Cliquer sur "Installer"

### 3. Ordre de Chargement
1. Aller dans l'onglet "Plugins"
2. Placer ENA après :
   - STALKER 2 : Scripts de base du jeu
   - Cyberpunk 2077 : redscript et CET
   - Starfield : Script Extender
   - RDR2 : Script Hook

### 4. Configuration Post-Installation
1. Lancer le jeu une première fois
2. Vérifier la création du fichier de configuration
3. Personnaliser `ena_config.json` selon vos besoins

## Résolution des Problèmes

### Problèmes Courants

#### 1. Conflit de Mods
```
Solution :
- Désactiver temporairement les autres mods
- Réactiver un par un pour identifier le conflit
- Ajuster l'ordre de chargement
```

#### 2. Fichiers Manquants
```
Solution :
- Vérifier l'installation dans Vortex
- Réinstaller le mod
- Vérifier les permissions des dossiers
```

#### 3. Erreurs de Script
```
Solution :
- Vérifier la compatibilité avec la version du jeu
- Mettre à jour les dépendances requises
- Consulter les logs dans le dossier du jeu
```

## Notes Importantes

### Compatibilité
- Vérifier la liste des mods compatibles
- Suivre l'ordre de chargement recommandé
- Utiliser la dernière version de Vortex

### Sauvegarde
- Sauvegarder vos fichiers avant l'installation
- Créer une nouvelle sauvegarde après l'installation
- Ne pas désinstaller en cours de partie

### Mise à Jour
- Désinstaller l'ancienne version avant la mise à jour
- Nettoyer les fichiers de configuration
- Suivre les instructions de migration si nécessaire

# Enhanced NPC Autonomous Plugin pour STALKER 2

## Description
Ce plugin ajoute un système de contrôle IA avancé pour les PNJ dans STALKER 2. Il permet une gestion autonome intelligente des personnages non-joueurs, avec des comportements adaptatifs et une prise de décision contextuelle.

## Fonctionnalités
- Système de contrôle unifié pour les PNJ
- Gestion intelligente des comportements
- Système de logs avancé pour le suivi des décisions
- Configuration flexible via fichiers JSON
- Archivage automatique des logs

## Installation
1. Assurez-vous que STALKER 2 est fermé
2. Exécutez le script d'installation :
   ```bash
   python install.py
   ```
3. Le plugin sera installé dans le dossier `bin/plugins/enhanced_npc_autonomous` du jeu

## Configuration
Le fichier de configuration se trouve dans `bin/plugins/enhanced_npc_autonomous/config/config.json`

Options principales :
- `ai_enabled`: Active/désactive l'IA (true/false)
- `log_level`: Niveau de détail des logs (INFO, DEBUG, WARNING, ERROR)
- `max_log_size_mb`: Taille maximale des fichiers de log en Mo
- `max_log_files`: Nombre maximum de fichiers de log à conserver
- `archive_days`: Nombre de jours avant archivage des logs

## Logs
Les logs sont stockés dans `bin/plugins/enhanced_npc_autonomous/logs/` :
- `ai_general.log`: Logs généraux du système
- `ai_decisions.log`: Décisions prises par l'IA
- `ai_combat.log`: Actions de combat
- `ai_state.log`: Changements d'état des PNJ

## Structure des fichiers
```
enhanced_npc_autonomous/
├── config/
│   └── config.json
├── logs/
│   ├── ai_general.log
│   ├── ai_decisions.log
│   ├── ai_combat.log
│   └── ai_state.log
├── player_ai/
│   ├── unified_player_system.py
│   └── ai_logger.py
└── plugin.info
```

## Désinstallation
Pour désinstaller le plugin, supprimez simplement le dossier `bin/plugins/enhanced_npc_autonomous` du répertoire du jeu.

## Support
En cas de problème :
1. Consultez les logs dans le dossier `logs`
2. Vérifiez la configuration dans `config.json`
3. Assurez-vous que tous les fichiers sont présents

## Contribuer
Les contributions sont les bienvenues ! N'hésitez pas à :
1. Forker le projet
2. Créer une branche pour votre fonctionnalité
3. Soumettre une pull request

## Licence
Ce plugin est distribué sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Crédits
Développé par l'équipe Codeium

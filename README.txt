ENA (Enhanced NPC Autonomous) - Guide Complet
==========================================

Table des matières :
1. Introduction
2. Installation
3. Configuration
4. Intégration aux Jeux
5. Modèles d'IA
6. Dépannage
7. FAQ

1. INTRODUCTION
--------------
ENA est un système avancé d'IA pour les PNJ (Personnages Non-Joueurs) qui améliore considérablement leur comportement dans les jeux vidéo. Le système utilise l'intelligence artificielle pour créer des PNJ plus réalistes et autonomes.

Fonctionnalités principales :
- Dialogues dynamiques et naturels
- Comportements autonomes
- Mémoire et apprentissage
- Routines quotidiennes réalistes
- Système économique dynamique
- Combat intelligent
- Interactions sociales complexes

2. INSTALLATION
--------------
A. Prérequis :
   - Python 3.8 ou supérieur
   - 16GB RAM minimum
   - GPU avec 8GB VRAM recommandé
   - LM Studio ou autre serveur de modèle local

B. Installation pas à pas :
   1. Téléchargez le dossier ENA
   2. Installez les dépendances :
      > pip install -r requirements.txt
   
   3. Configuration du modèle local :
      - Installez LM Studio
      - Téléchargez un modèle (Mistral 7B recommandé)
      - Copiez le modèle dans : models/lmstudio/model/

   4. Structure des dossiers :
      Enhanced NPC Autonomous/
      ├── src/                    # Code source
      ├── data/                   # Données
      ├── models/                 # Modèles d'IA
      ├── examples/               # Exemples d'intégration
      └── docs/                   # Documentation

3. CONFIGURATION
---------------
A. Configuration du serveur (config.json) :
   {
     "server": {
       "host": "localhost",
       "port": 8000
     },
     "model": {
       "type": "lmstudio",
       "settings": {
         "temperature": 0.7
       }
     }
   }

B. Configuration des PNJ (data/npc_templates.json) :
   - Personnalité
   - Routines
   - Compétences
   - Relations

4. INTÉGRATION AUX JEUX
----------------------
A. Unity :
   1. Copiez examples/unity/ dans votre projet
   2. Ajoutez le préfab GameLauncher
   3. Configurez NPCManager

B. Unreal Engine :
   1. Copiez examples/unreal/ dans Source/
   2. Incluez NPCManager.h
   3. Initialisez dans votre GameMode

C. Autres Jeux :
   1. Minecraft : Copiez dans plugins/
   2. Skyrim : Installez dans Data/SKSE/Plugins/
   3. GTA V : Copiez dans scripts/
   4. RDR2 : Installez dans scripts/
   5. Fallout 4 : Copiez dans Data/F4SE/Plugins/

5. MODÈLES D'IA
--------------
A. LM Studio (Recommandé) :
   1. Installation :
      - Téléchargez LM Studio
      - Installez un modèle (Mistral 7B recommandé)
   
   2. Configuration :
      - Port : 1234 (défaut)
      - Quantization : 4-bit
      - Context length : 4096

B. Alternatives :
   - Ollama
   - GPT4All
   - LocalAI

6. DÉPANNAGE
-----------
A. Problèmes courants :
   1. "Modèle non trouvé" :
      - Vérifiez le chemin du modèle
      - Vérifiez les permissions

   2. "Erreur de connexion" :
      - Vérifiez que le serveur est lancé
      - Vérifiez le port

   3. "Mémoire insuffisante" :
      - Utilisez la quantization 4-bit
      - Réduisez la taille du contexte

B. Logs :
   - Serveur : logs/server.log
   - API : logs/api.log
   - NPC : logs/npc.log

7. FAQ
------
Q: Quelle configuration minimale ?
R: Python 3.8+, 16GB RAM, GPU 8GB VRAM recommandé

Q: Quels modèles sont supportés ?
R: Tous les modèles GGUF/GGML via LM Studio

Q: Comment améliorer les performances ?
R: Utilisez la quantization 4-bit, ajustez context_length

Q: Comment personnaliser les comportements ?
R: Modifiez data/npc_templates.json

UTILISATION RAPIDE
-----------------
1. Démarrer le serveur :
   > python -m src.api

2. Vérifier l'installation :
   > python -m src.tools.test_model

3. Intégrer dans votre jeu :
   - Suivez le guide d'intégration spécifique
   - Testez avec un PNJ simple
   - Ajoutez progressivement des fonctionnalités

SUPPORT
-------
- Documentation : docs/
- Issues : GitHub Issues
- Contact : support@ena-project.com

LICENCE
-------
MIT License - Voir LICENSE pour plus de détails

Note : Ce projet est en développement actif. Consultez régulièrement les mises à jour pour les nouvelles fonctionnalités et améliorations.

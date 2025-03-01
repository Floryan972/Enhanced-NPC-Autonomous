# Enhanced NPC Autonomous

Ce projet améliore l'autonomie des PNJ dans STALKER 2 Heart of Chornobyl en utilisant l'intelligence artificielle pour créer des comportements plus réalistes et dynamiques.

## Fonctionnalités

- Comportements PNJ améliorés et plus réalistes
- Système de factions dynamique
- Gestion avancée des quêtes
- Interactions PNJ-PNJ et PNJ-joueur plus naturelles
- Système de personnalité pour les PNJ
- Gestion des événements du monde

## Prérequis

- Python 3.8 ou supérieur
- STALKER 2 Heart of Chornobyl
- 8 Go de RAM minimum
- Espace disque : 5 Go minimum (incluant le modèle d'IA)

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/Floryan972/Enhanced-NPC-Autonomous.git
cd Enhanced-NPC-Autonomous
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Téléchargez le modèle d'IA :
   - Rendez-vous sur [TheBloke/Qwen2-7B-Instruct-GGUF](https://huggingface.co/TheBloke/Qwen2-7B-Instruct-GGUF/blob/main/qwen2-7b-instruct-v0.6.Q4_K_M.gguf)
   - Téléchargez le fichier `qwen2-7b-instruct-v0.6.Q4_K_M.gguf`
   - Placez-le dans le dossier `models/` du projet

4. Configurez le mod :
   - Copiez le fichier `config/ena_config.example.json` vers `config/ena_config.json`
   - Modifiez les paramètres selon vos préférences

## Utilisation

1. Lancez le script d'activation :
```bash
python activate_ai.py
```

2. Démarrez STALKER 2 et chargez votre partie

3. Le mod s'active automatiquement et améliore le comportement des PNJ

## Configuration

Vous pouvez personnaliser le comportement des PNJ en modifiant les fichiers suivants :
- `config/npc_personalities.json` : Définit les traits de personnalité des PNJ
- `config/species_behaviors.json` : Configure les comportements spécifiques
- `config/player_control.json` : Ajuste l'interaction avec le joueur

## Structure du projet

- `models/` : Dossier contenant les modèles d'IA (non inclus dans le dépôt)
- `src/` : Code source du projet
  - `ai_core/` : Moteur d'IA principal
  - `npc/` : Système unifié de gestion des PNJ
  - `player_control/` : Interface avec le joueur
- `config/` : Fichiers de configuration
- `docs/` : Documentation détaillée
- `tests/` : Tests unitaires et d'intégration

## Contribution

Les contributions sont les bienvenues ! Pour contribuer :
1. Forkez le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Support

Si vous rencontrez des problèmes :
1. Consultez la [documentation](docs/integration_guide.md)
2. Vérifiez les [issues existantes](https://github.com/Floryan972/Enhanced-NPC-Autonomous/issues)
3. Ouvrez une nouvelle issue si nécessaire

## Remerciements

- L'équipe de STALKER 2 pour leur jeu incroyable
- La communauté des modders pour leur soutien
- Les contributeurs du projet Qwen2 pour leur modèle d'IA

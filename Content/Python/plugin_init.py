"""
Script d'initialisation pour le plugin Enhanced NPC Autonomous dans UE4
"""
import unreal
import sys
from pathlib import Path

def initialize():
    """Initialise le plugin dans UE4"""
    try:
        # Chemin du plugin Python
        plugin_path = Path("D:/ELECTRONIC'S ARTS/STALKER 2 Heart of Chornobyl/bin/plugins/enhanced_npc_autonomous")
        
        # Ajoute le chemin au PYTHONPATH
        if str(plugin_path) not in sys.path:
            sys.path.append(str(plugin_path))
        
        # Import et initialisation du plugin
        from plugin_loader import initialize_plugin
        controller, ai_logger = initialize_plugin()
        
        # Enregistre les commandes dans l'UE
        @unreal.uclass()
        class AICommands:
            @unreal.ufunction(exec=True)
            def toggle_ai(self):
                """Active/désactive l'IA (touche \)"""
                controller.toggle_ai_mode()
            
            @unreal.ufunction(exec=True)
            def ai_status(self):
                """Affiche le statut de l'IA (touche [)"""
                controller.print_status()
            
            @unreal.ufunction(exec=True)
            def ai_add_enemy(self):
                """Ajoute un ennemi (touche ])"""
                controller.add_enemy()
        
        # Crée une instance des commandes
        commands = AICommands()
        
        # Enregistre les touches
        input_settings = unreal.get_default_object(unreal.InputSettings)
        input_settings.add_action_mapping("toggle_ai", "\\", False, False, False, False)
        input_settings.add_action_mapping("ai_status", "[", False, False, False, False)
        input_settings.add_action_mapping("ai_add_enemy", "]", False, False, False, False)
        
        unreal.log("Plugin Enhanced NPC Autonomous initialisé avec succès")
        return True
        
    except Exception as e:
        unreal.log_error(f"Erreur lors de l'initialisation du plugin: {e}")
        return False

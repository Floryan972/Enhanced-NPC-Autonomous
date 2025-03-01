from ena.core.audio_input import audio_manager
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def on_speech_recognized(text: str, confidence: float):
    """Appelé lorsque la parole est reconnue"""
    print(f"Parole reconnue (confiance: {confidence:.2%}) : {text}")
    
    # Afficher l'historique des commandes si demandé
    if "historique" in text.lower():
        show_command_history()

def on_error(error: str):
    """Appelé lorsqu'une erreur survient"""
    print(f"Erreur : {error}")
    
def on_volume_change(volume: float):
    """Appelé lorsque le niveau sonore change"""
    bars = int(volume * 20)
    print(f"Niveau sonore : [{'|' * bars}{' ' * (20-bars)}] {volume:.2%}")
    
def show_command_history():
    """Affiche l'historique des commandes vocales"""
    print("\n=== Historique des commandes ===")
    for cmd in audio_manager.get_command_history():
        print(f"{cmd.timestamp.strftime('%H:%M:%S')} - "
              f"'{cmd.text}' (confiance: {cmd.confidence:.2%})")
    print("==============================\n")

# Commandes rapides
def on_stop(text: str, confidence: float):
    """Réaction à la commande 'stop'"""
    print("Commande rapide 'stop' détectée !")
    audio_manager.stop_listening()

def on_salut(text: str, confidence: float):
    """Réaction à la commande 'salut'"""
    print("Bonjour ! Comment puis-je vous aider ?")

def on_action(text: str, confidence: float):
    """Réaction à une commande d'action"""
    print(f"Action rapide détectée ! ({text})")

def main():
    print("=== Exemple Amélioré d'Entrée Microphone ===")
    print("Fonctionnalités disponibles :")
    print("1. Commandes rapides :")
    print("   - 'stop' : arrête le programme")
    print("   - 'salut' : salutation rapide")
    print("   - 'action' : exemple d'action rapide")
    print("2. Mot d'activation : 'assistant' (pour les autres commandes)")
    print("3. Surveillance du niveau sonore")
    print("4. Historique des commandes (dites 'historique')")
    print("\nParlez dans votre microphone en français")
    print("Appuyez sur Ctrl+C pour quitter")
    print("=======================================")
    
    # Configurer le gestionnaire audio
    audio_manager.set_wake_word("assistant", required=True)
    audio_manager.set_noise_threshold(500)
    audio_manager.set_volume_callback(on_volume_change, notification_interval=0.5)
    
    # Ajouter les commandes rapides
    audio_manager.add_active_command("stop", on_stop)
    audio_manager.add_active_command("salut", on_salut)
    audio_manager.add_active_command("action", on_action)
    
    # Démarrer l'écoute de la parole
    audio_manager.start_listening(
        callback=on_speech_recognized,
        error_callback=on_error,
        language="fr-FR"
    )
    
    try:
        # Garder le programme en cours d'exécution
        while audio_manager.is_listening:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nArrêt de l'entrée microphone...")
        audio_manager.stop_listening()

if __name__ == "__main__":
    main()

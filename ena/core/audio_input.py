import speech_recognition as sr
import sounddevice as sd
import numpy as np
import threading
import queue
import time
from typing import Optional, Callable, List, Dict, Set
import logging
from datetime import datetime
from collections import deque
import webrtcvad  # Pour la détection d'activité vocale
import wave
import audioop
import array

logger = logging.getLogger(__name__)

class VoiceCommand:
    def __init__(self, text: str, confidence: float, timestamp: datetime):
        self.text = text
        self.confidence = confidence
        self.timestamp = timestamp

class AudioInputManager:
    def __init__(self):
        self._recognizer = sr.Recognizer()
        self._audio_queue = queue.Queue()
        self._is_listening = False
        self._callback = None
        self._error_callback = None
        self._wake_word = "assistant"
        self._is_wake_word_required = True
        self._command_history = deque(maxlen=100)
        self._noise_threshold = 300
        self._volume_callback = None
        self._last_volume_notification = 0
        self._volume_notification_interval = 1.0
        
        # Paramètres pour la reconnaissance instantanée
        self._vad = webrtcvad.Vad(3)  # Niveau d'agressivité de la détection vocale (0-3)
        self._buffer_queue = queue.Queue()
        self._is_speaking = False
        self._current_phrase = []
        self._sample_rate = 16000
        self._frame_duration = 30  # ms
        self._min_phrase_duration = 0.3  # secondes
        self._silence_duration = 0.5  # secondes
        self._last_speech_time = 0
        self._active_commands = set()  # Commandes actuellement actives
        
    def add_active_command(self, command: str, callback: Callable[[str, float], None]):
        """
        Ajouter une commande vocale active qui sera détectée instantanément.
        
        Args:
            command: La commande à détecter
            callback: Fonction à appeler quand la commande est détectée
        """
        self._active_commands.add((command.lower(), callback))
        
    def remove_active_command(self, command: str):
        """Supprimer une commande vocale active"""
        command = command.lower()
        self._active_commands = {(cmd, cb) for cmd, cb in self._active_commands 
                               if cmd != command}
        
    def set_wake_word(self, word: str, required: bool = True):
        """
        Définir le mot d'activation et si il est requis.
        
        Args:
            word: Mot qui déclenchera l'écoute active
            required: Si True, le mot d'activation est nécessaire
        """
        self._wake_word = word.lower()
        self._is_wake_word_required = required
        
    def set_noise_threshold(self, threshold: int):
        """
        Définir le seuil de détection du bruit.
        
        Args:
            threshold: Valeur du seuil (0-1000)
        """
        self._noise_threshold = max(0, min(1000, threshold))
        
    def set_volume_callback(self, callback: Callable[[float], None], 
                          notification_interval: float = 1.0):
        """
        Définir une fonction de rappel pour le niveau sonore.
        
        Args:
            callback: Fonction appelée avec le niveau sonore (0.0 - 1.0)
            notification_interval: Intervalle minimum entre les notifications
        """
        self._volume_callback = callback
        self._volume_notification_interval = notification_interval
        
    def get_command_history(self) -> List[VoiceCommand]:
        """Récupérer l'historique des commandes vocales"""
        return list(self._command_history)
        
    def start_listening(self, 
                       callback: Callable[[str, float], None],
                       error_callback: Optional[Callable[[str], None]] = None,
                       language: str = "fr-FR"):
        """
        Commence à écouter l'entrée du microphone.
        
        Args:
            callback: Fonction à appeler lorsque la parole est reconnue
            error_callback: Fonction à appeler en cas d'erreur
            language: Code de langue pour la reconnaissance vocale
        """
        if self._is_listening:
            logger.warning("Déjà en train d'écouter l'entrée du microphone")
            return
            
        self._callback = callback
        self._error_callback = error_callback
        self._is_listening = True
        
        # Démarrer les threads
        threading.Thread(target=self._audio_processing_loop,
                       args=(language,),
                       daemon=True).start()
                       
        threading.Thread(target=self._monitor_volume,
                       daemon=True).start()
        
    def stop_listening(self):
        """Arrêter l'écoute du microphone"""
        self._is_listening = False
        
    def _process_audio_chunk(self, audio_chunk: bytes, language: str):
        """Traite un segment audio pour la reconnaissance instantanée"""
        is_speech = self._vad.is_speech(audio_chunk, self._sample_rate)
        current_time = time.time()
        
        if is_speech:
            self._current_phrase.append(audio_chunk)
            self._last_speech_time = current_time
            if not self._is_speaking:
                self._is_speaking = True
                logger.debug("Début de la parole détectée")
        elif self._is_speaking:
            # Vérifier si le silence est assez long pour terminer la phrase
            if current_time - self._last_speech_time > self._silence_duration:
                self._is_speaking = False
                if len(self._current_phrase) > 0:
                    self._process_phrase(b''.join(self._current_phrase), language)
                self._current_phrase = []
                
    def _process_phrase(self, audio_data: bytes, language: str):
        """Traite une phrase complète pour la reconnaissance"""
        try:
            # Convertir les données audio au format attendu par speech_recognition
            audio = sr.AudioData(audio_data, self._sample_rate, 2)
            
            # Reconnaissance rapide pour les commandes actives
            text = self._recognizer.recognize_google(audio, 
                                                   language=language,
                                                   show_all=True)
            
            if text and isinstance(text, dict) and 'alternative' in text:
                best_match = text['alternative'][0]
                recognized_text = best_match['transcript'].lower()
                confidence = best_match.get('confidence', 0.0)
                
                # Vérifier les commandes actives
                for command, cmd_callback in self._active_commands:
                    if command in recognized_text:
                        cmd_callback(recognized_text, confidence)
                
                # Vérifier le mot d'activation si nécessaire
                if (not self._is_wake_word_required or 
                    self._wake_word in recognized_text):
                    
                    command = VoiceCommand(recognized_text, 
                                         confidence,
                                         datetime.now())
                    self._command_history.append(command)
                    
                    if self._callback:
                        self._callback(recognized_text, confidence)
                        
        except sr.UnknownValueError:
            pass  # Ignorer les phrases non reconnues pour plus de réactivité
        except Exception as e:
            logger.error(f"Erreur de reconnaissance : {str(e)}")
            
    def _audio_processing_loop(self, language: str):
        """Boucle principale de traitement audio"""
        try:
            def audio_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Erreur audio: {status}")
                    return
                    
                # Convertir en format attendu par WebRTC VAD
                audio_chunk = (indata * 32767).astype(np.int16).tobytes()
                
                # Découper en fragments de la bonne taille pour VAD
                frame_length = int(self._sample_rate * self._frame_duration / 1000)
                for i in range(0, len(audio_chunk), frame_length * 2):
                    frame = audio_chunk[i:i + frame_length * 2]
                    if len(frame) == frame_length * 2:  # Ignorer le dernier fragment incomplet
                        self._process_audio_chunk(frame, language)

            with sd.InputStream(callback=audio_callback,
                              channels=1,
                              samplerate=self._sample_rate,
                              dtype=np.float32):
                while self._is_listening:
                    sd.sleep(100)
                    
        except Exception as e:
            logger.error(f"Erreur dans la boucle de traitement audio : {str(e)}")
            if self._error_callback:
                self._error_callback(f"Erreur de traitement audio : {str(e)}")
                
    def _monitor_volume(self):
        """Surveille le niveau sonore en continu"""
        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning(f"Erreur audio: {status}")
                return
                
            volume_norm = np.linalg.norm(indata) * 10
            
            current_time = time.time()
            if (self._volume_callback and 
                current_time - self._last_volume_notification >= self._volume_notification_interval):
                self._volume_callback(min(1.0, volume_norm / self._noise_threshold))
                self._last_volume_notification = current_time

        try:
            with sd.InputStream(callback=audio_callback):
                while self._is_listening:
                    sd.sleep(100)
        except Exception as e:
            logger.error(f"Erreur dans le monitoring du volume: {str(e)}")

    @property
    def is_listening(self) -> bool:
        """Vérifier si l'écoute du microphone est active"""
        return self._is_listening

# Instance singleton
audio_manager = AudioInputManager()

import win32gui
import win32process
import win32api
import win32con
import psutil
import logging
from typing import Dict, Any, Optional
import struct
import time

class Stalker2GameHook:
    """Interface de bas niveau pour communiquer avec STALKER 2"""
    
    GAME_WINDOW_NAME = "S.T.A.L.K.E.R. 2: Heart of Chornobyl"
    PROCESS_NAME = "Stalker2.exe"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.game_hwnd = None
        self.process_id = None
        self.process_handle = None
        self.base_address = None

    def find_game_window(self) -> bool:
        """Trouve la fenêtre du jeu"""
        try:
            self.game_hwnd = win32gui.FindWindow(None, self.GAME_WINDOW_NAME)
            if self.game_hwnd:
                _, self.process_id = win32process.GetWindowThreadProcessId(self.game_hwnd)
                self.process_handle = win32api.OpenProcess(
                    win32con.PROCESS_VM_READ | win32con.PROCESS_VM_WRITE | win32con.PROCESS_VM_OPERATION,
                    False,
                    self.process_id
                )
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche de la fenêtre du jeu: {e}")
            return False

    def get_player_position(self) -> Optional[Dict[str, float]]:
        """Lit la position du joueur en mémoire"""
        try:
            # Les offsets devront être mis à jour en fonction de la version du jeu
            player_pos_offset = 0x0  # À déterminer
            pos_data = self.read_memory(self.base_address + player_pos_offset, 12)
            if pos_data:
                x, y, z = struct.unpack('fff', pos_data)
                return {"x": x, "y": y, "z": z}
            return None
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture de la position: {e}")
            return None

    def get_player_stats(self) -> Optional[Dict[str, float]]:
        """Lit les statistiques du joueur"""
        try:
            # Les offsets devront être mis à jour
            health_offset = 0x0  # À déterminer
            stamina_offset = 0x0  # À déterminer
            radiation_offset = 0x0  # À déterminer

            health = self.read_memory(self.base_address + health_offset, 4)
            stamina = self.read_memory(self.base_address + stamina_offset, 4)
            radiation = self.read_memory(self.base_address + radiation_offset, 4)

            if all([health, stamina, radiation]):
                return {
                    "health": struct.unpack('f', health)[0],
                    "stamina": struct.unpack('f', stamina)[0],
                    "radiation": struct.unpack('f', radiation)[0]
                }
            return None
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture des stats: {e}")
            return None

    def simulate_input(self, input_type: str, value: Any):
        """Simule une entrée utilisateur"""
        try:
            if input_type == "movement":
                self._simulate_movement(value)
            elif input_type == "action":
                self._simulate_action(value)
            elif input_type == "combat":
                self._simulate_combat(value)
        except Exception as e:
            self.logger.error(f"Erreur lors de la simulation d'entrée: {e}")

    def _simulate_movement(self, direction: Dict[str, float]):
        """Simule le mouvement du joueur"""
        # Utilise SendInput pour simuler les touches de mouvement
        keys = []
        if direction["forward"] > 0:
            keys.append(win32con.VK_W)
        if direction["backward"] > 0:
            keys.append(win32con.VK_S)
        if direction["left"] > 0:
            keys.append(win32con.VK_A)
        if direction["right"] > 0:
            keys.append(win32con.VK_D)

        for key in keys:
            win32api.SendMessage(self.game_hwnd, win32con.WM_KEYDOWN, key, 0)
            time.sleep(0.05)
            win32api.SendMessage(self.game_hwnd, win32con.WM_KEYUP, key, 0)

    def _simulate_combat(self, action: Dict[str, Any]):
        """Simule les actions de combat"""
        if action["type"] == "shoot":
            # Clic gauche pour tirer
            win32api.SendMessage(self.game_hwnd, win32con.WM_LBUTTONDOWN, 0, 0)
            time.sleep(0.05)
            win32api.SendMessage(self.game_hwnd, win32con.WM_LBUTTONUP, 0, 0)
        elif action["type"] == "aim":
            # Clic droit pour viser
            win32api.SendMessage(self.game_hwnd, win32con.WM_RBUTTONDOWN, 0, 0)
            if not action["hold"]:
                time.sleep(0.05)
                win32api.SendMessage(self.game_hwnd, win32con.WM_RBUTTONUP, 0, 0)

    def read_memory(self, address: int, size: int) -> Optional[bytes]:
        """Lit la mémoire du processus"""
        try:
            buffer = win32process.ReadProcessMemory(self.process_handle, address, size)
            return buffer
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture de la mémoire: {e}")
            return None

    def write_memory(self, address: int, data: bytes) -> bool:
        """Écrit dans la mémoire du processus"""
        try:
            win32process.WriteProcessMemory(self.process_handle, address, data, len(data))
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'écriture en mémoire: {e}")
            return False

    def cleanup(self):
        """Nettoie les ressources"""
        if self.process_handle:
            win32api.CloseHandle(self.process_handle)

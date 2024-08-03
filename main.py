# ============================================
# Mario Party Scanner
# Author: S Hanegan (naylahanegan@gmail.com)
# Date: 5/4/2024
# License: MIT
# ============================================

import customtkinter
import os
from PIL import Image
import tkinter as tk
import win32gui
import dolphin_memory_engine

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mario Party Scanner")
        self.geometry("1330x780")

        customtkinter.set_appearance_mode("Dark")

        self.home_frame = customtkinter.CTkFrame(self, corner_radius=12, fg_color=("gray75", "gray25"), width=1310, height=760)
        self.home_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.turn_label = customtkinter.CTkLabel(self.home_frame, text="", font=("Helvetica", 32, "bold"))
        self.turn_label.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.update_turn_label()

    def window_enumeration_handler(self, hwnd, top_windows):
        top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

    def find_window_by_substring(self, substring):
        top_windows = []
        win32gui.EnumWindows(self.window_enumeration_handler, top_windows)
        for hwnd, window_text in top_windows:
            if substring in window_text:
                return hwnd, window_text
        return None, None

    def check_emulator_window(self):
        hwnd, window_text = self.find_window_by_substring("Dolphin MPN")
        if hwnd:
            return "Dolphin"
        hwnd, window_text = self.find_window_by_substring("Dolphin")
        if hwnd:
            return "Dolphin"
        return None

    def check_game_id(self):
        try:
            game_id = dolphin_memory_engine.read_bytes(0x80000000, 6)
            if game_id:
                return game_id.decode("utf-8")
        except:
            return None

    def get_current_turn(self, game_id):
        scene_id = self.get_scene_id(game_id)
        address_map = {
            "GMPE01": (0x8018FCFC, ["89", "90", "91", "92", "93", "94"]),
            "GP5E01": (0x8022A494, ["118", "120", "122", "124", "126", "128", "130"]),
            "GP6E01": (0x80265B74, ["123", "124", "125", "126", "127", "128"]),
            "GP7E01": (0x8029151C, ["122", "123", "124", "125", "126", "127"]),
            "RM8E01": (0x80228764, ["16", "17", "18", "19", "20", "21"])
        }
        if game_id in address_map and scene_id in address_map[game_id][1]:
            try:
                current_turn = dolphin_memory_engine.read_bytes(address_map[game_id][0], 1)
                current_turn_str = ''.join(f'{byte:02x}' for byte in current_turn).lstrip('0')
                return str(int(current_turn_str, 16)) or "0"
            except:
                return "0"
        return "0"

    def get_final_turn(self, game_id):
        scene_id = self.get_scene_id(game_id)
        address_map = {
            "GMPE01": (0x8018FCFD, ["89", "90", "91", "92", "93", "94"]),
            "GP5E01": (0x8022A495, ["118", "120", "122", "124", "126", "128", "130"]),
            "GP6E01": (0x80265B75, ["123", "124", "125", "126", "127", "128"]),
            "GP7E01": (0x8029151D, ["122", "123", "124", "125", "126", "127"]),
            "RM8E01": (0x80228765, ["16", "17", "18", "19", "20", "21"])
        }
        if game_id in address_map and scene_id in address_map[game_id][1]:
            try:
                final_turn = dolphin_memory_engine.read_bytes(address_map[game_id][0], 1)
                final_turn_str = ''.join(f'{byte:02x}' for byte in final_turn).lstrip('0')
                return str(int(final_turn_str, 16)) or "20"
            except:
                return "20"
        return "20"

    def get_scene_id(self, game_id):
        scene_id_map = {
            "GMPE01": 0x801D3CE3,
            "GP5E01": 0x80288863,
            "GP6E01": 0x802C0257,
            "GP7E01": 0x802F2F3F,
            "RM8E01": 0x802CD223
        }
        if game_id in scene_id_map:
            try:
                scene_id_bytes = dolphin_memory_engine.read_bytes(scene_id_map[game_id], 1)
                scene_id_str = ''.join(f'{byte:02x}' for byte in scene_id_bytes).lstrip('0')
                return str(int(scene_id_str, 16)) or "0"
            except:
                return "0"
        return "0"

    def update_turn_label(self):
        if self.check_emulator_window() == "Dolphin":
            dolphin_memory_engine.hook()

        game_id = self.check_game_id()
        if game_id:
            current_turn = self.get_current_turn(game_id)
            final_turn = self.get_final_turn(game_id)
            self.turn_label.configure(text=f"Turn: {current_turn} / {final_turn}")
        else:
            self.turn_label.configure(text="Game not detected")

        self.after(500, self.update_turn_label)

if __name__ == "__main__":
    app = App()
    app.mainloop()
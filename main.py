import customtkinter
import os
from PIL import Image, ImageTk
import tkinter as tk
import win32gui
import pygetwindow as gw
import json
import functions
import dolphin_memory_engine
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigFileHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app

    def on_modified(self, event):
        if event.src_path.endswith("names.json"):
            print("names.json has been updated. Reloading...")
            self.app.load_name_overrides()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        try:
            os.mkdir("data")
        except:
            pass

        self.title("Mario Party Scanner")
        self.geometry("1330x800")

        self.ensure_config_exists()
        self.load_name_overrides()
        customtkinter.set_appearance_mode("Dark")

        self.home_frame = customtkinter.CTkFrame(self, corner_radius=12, fg_color=("gray75", "gray25"), width=1310, height=780)
        self.home_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.turn_label = customtkinter.CTkLabel(self.home_frame, text="", font=("Helvetica", 32, "bold"))
        self.turn_label.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Configure grid columns to be evenly spaced
        for i in range(4):
            self.home_frame.grid_columnconfigure(i, weight=1)

        # Image labels and character name labels
        self.image_labels = []
        self.name_labels = []
        for i in range(4):
            img_label = customtkinter.CTkLabel(self.home_frame, text="", width=150, height=150, corner_radius=8)
            img_label.grid(row=1, column=i, padx=10, pady=5, sticky="nsew")
            self.image_labels.append(img_label)

            name_label = customtkinter.CTkLabel(self.home_frame, text="", font=("Helvetica", 24))
            name_label.grid(row=2, column=i, padx=10, pady=5, sticky="nsew")
            self.name_labels.append(name_label)

        self.cached_turn = None
        self.cached_final_turn = None

        self.update_turn_label()

        # Start file monitoring
        self.start_file_monitoring()

    def ensure_config_exists(self):
        """Create a default names.json file if it doesn't exist."""
        config_path = "data/names.json"
        if not os.path.exists(config_path):
            default_names = {
                "Player1": "",
                "Player2": "",
                "Player3": "",
                "Player4": ""
            }
            try:
                with open(config_path, "w") as file:
                    json.dump(default_names, file, indent=4)
            except Exception as e:
                print(f"Error creating names.json: {e}")

    def load_name_overrides(self):
        self.name_overrides = {}
        try:
            with open("data/names.json", "r") as file:
                data = json.load(file)
                if not isinstance(data, dict):
                    print("names.json is not a valid JSON object.")
                    return {}
                for key, name in data.items():
                    if name:  # Only update if name is not blank
                        self.name_overrides[key] = name
        except FileNotFoundError:
            print("names.json file not found.")
        except json.JSONDecodeError:
            print("Error decoding names.json.")

    def start_file_monitoring(self):
        event_handler = ConfigFileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(os.path.abspath("data/names.json")), recursive=False)
        observer.start()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        # Stop the observer when the application closes
        self.observer.stop()
        self.observer.join()
        self.destroy()

    def window_enumeration_handler(self, hwnd, top_windows):
        top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

    def is_dolphin_netplay_running(self):
        windows = gw.getWindowsWithTitle('NetPlay')  # Adjust the title if needed
        return windows[0] if windows else None

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
        if game_id in address_map:
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
        if game_id in address_map:
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

            # Handle turn reset to 255
            if current_turn == "255" and self.cached_turn != "255":
                current_turn = self.cached_turn

            # Cache previous turn if current turn resets to 0
            if current_turn == "0" and self.cached_turn != "0":
                current_turn = self.cached_turn

            # Update cache only if the new value is valid
            if current_turn != "0":
                self.cached_turn = current_turn

            # Fallback to cached value if final turn is invalid
            if final_turn is None:
                final_turn = self.cached_final_turn

            if current_turn and final_turn:
                self.cached_final_turn = final_turn

                self.turn_label.configure(text=f"Turn: {current_turn} / {final_turn}")
                self.write_turn_to_file(current_turn, final_turn)
                self.update_images(game_id)

                # Show or hide portraits and names based on turn count
                if current_turn == "0":
                    for img_label, name_label in zip(self.image_labels, self.name_labels):
                        img_label.grid_forget()
                        name_label.grid_forget()
                else:
                    for img_label, name_label in zip(self.image_labels, self.name_labels):
                        img_label.grid(row=1, column=self.image_labels.index(img_label), padx=10, pady=10, sticky="nsew")
                        name_label.grid(row=2, column=self.name_labels.index(name_label), padx=10, pady=5, sticky="nsew")
            else:
                self.turn_label.configure(text="Game not detected")
                # Hide portraits and names if no game is detected
                for img_label, name_label in zip(self.image_labels, self.name_labels):
                    img_label.grid_forget()
                    name_label.grid_forget()

        else:
            self.turn_label.configure(text="Game not detected")
            # Hide portraits and names if no game is detected
            for img_label, name_label in zip(self.image_labels, self.name_labels):
                img_label.grid_forget()
                name_label.grid_forget()

        self.after(500, self.update_turn_label)

    def write_turn_to_file(self, current_turn, final_turn):
        with open("data/turn.txt", "w") as f:
            f.write(f"Turn: {current_turn} / {final_turn}\n")

    def update_images(self, game_id):
        # Retrieve character IDs
        character_ids = self.get_character_id(game_id)

        # Generate image paths based on character IDs
        if game_id == "GMPE01":
            image_paths = [functions.resource_path(f"assets/mp4/{character_id}.png") for character_id in character_ids]
        elif game_id == "GP5E01":
            image_paths = [functions.resource_path(f"assets/mp5/{character_id}.png") for character_id in character_ids]
        elif game_id == "GP6E01":
            image_paths = [functions.resource_path(f"assets/mp6/{character_id}.png") for character_id in character_ids]
        elif game_id == "GP7E01":
            image_paths = [functions.resource_path(f"assets/mp7/{character_id}.png") for character_id in character_ids]
        elif game_id == "RM8E01":
            image_paths = [functions.resource_path(f"assets/mp8/{character_id}.png") for character_id in character_ids]

        for i, img_label in enumerate(self.image_labels):
            # Check if index is within bounds
            if i < len(image_paths):
                image_path = image_paths[i]

                # Load and display image
                if image_path and os.path.exists(image_path):
                    image = Image.open(image_path)
                    image = image.resize((150, 150), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    img_label.configure(image=photo)
                    img_label.image = photo  # Keep a reference to avoid garbage collection
                else:
                    img_label.configure(image=None)

                # Update character name
                if i < len(self.name_labels):
                    character_name = self.get_character_name(character_ids[i], i)
                    self.name_labels[i].configure(text=character_name)
            else:
                img_label.configure(image=None)
                if i < len(self.name_labels):
                    self.name_labels[i].configure(text="")

    def get_character_name(self, character_id, player_index):
        character_map = {
            "mario": "Mario",
            "luigi": "Luigi",
            "peach": "Peach",
            "yoshi": "Yoshi",
            "wario": "Wario",
            "dk": "Donkey Kong",
            "daisy": "Daisy",
            "waluigi": "Waluigi",
            "boo": "Boo",
            "koopakid": "Koopa Kid",
            "toad": "Toad",
            "toadette": "Toadette",
            "drybones": "Dry Bones",
            "birdo": "Birdo",
            "blooper": "Blooper",
            "hammerbro": "Hammer Bro"
        }
        
        # Get the default name
        default_name = character_map.get(character_id, "Unknown")
        
        # Check if there is an override for this player
        player_key = f"Player{player_index + 1}"
        return self.name_overrides.get(player_key, default_name).capitalize()

    def get_character_id(self, game_id):
        address_map = {
            "GMPE01": [0x8018FC11, 0x8018FC1B, 0x8018FC25, 0x8018FC2F],
            "GP5E01": [0x8022A049, 0x8022A053, 0x8022A05D, 0x8022A067],
            "GP6E01": [0x80265729, 0x80265733, 0x8026573D, 0x80265747],
            "GP7E01": [0x80290C49, 0x80290C53, 0x80290C5D, 0x80290C67],
            "RM8E01": [0x802282D1, 0x802282DB, 0x802282E5, 0x802282EF]
        }

        if game_id == "GMPE01":
            character_map = {
                "00": "mario",
                "01": "luigi",
                "02": "peach",
                "03": "yoshi",
                "04": "wario",
                "05": "dk",
                "06": "daisy",
                "07": "waluigi"
            }
        elif game_id == "GP5E01":
            character_map = {
                "00": "mario",
                "01": "luigi",
                "02": "peach",
                "03": "yoshi",
                "04": "wario",
                "05": "daisy",
                "06": "waluigi",
                "07": "toad",
                "08": "boo",
                "09": "koopakid"
            }

        elif game_id == "GP6E01":
            character_map = {
                "00": "mario",
                "01": "luigi",
                "02": "peach",
                "03": "yoshi",
                "04": "wario",
                "05": "daisy",
                "06": "waluigi",
                "07": "toad",
                "08": "boo",
                "09": "koopakid",
                "0A": "toadette"
            }

        elif game_id == "GP7E01":
            character_map = {
                "00": "mario",
                "01": "luigi",
                "02": "peach",
                "03": "yoshi",
                "04": "wario",
                "05": "daisy",
                "06": "waluigi",
                "07": "toad",
                "08": "boo",
                "09": "toadette",
                "0A": "birdo",
                "0B": "drybones"
            }

        elif game_id == "RM8E01":
            character_map = {
                "00": "mario",
                "01": "luigi",
                "02": "peach",
                "03": "yoshi",
                "04": "wario",
                "05": "daisy",
                "06": "waluigi",
                "07": "toad",
                "08": "boo",
                "09": "toadette",
                "0A": "birdo",
                "0B": "drybones",
                "0C": "hammerbro",
                "0D": "blooper"
            }

        def read_character(address):
            try:
                bytes_ = dolphin_memory_engine.read_bytes(address, 1)
                hex_str = ''.join(f'{byte:02x}' for byte in bytes_).zfill(2).upper()
                return character_map.get(hex_str, "mario")
            except:
                return "mario"

        # Ensure game_id is valid and retrieve addresses
        addresses = address_map.get(game_id, [])
        characters = [read_character(addr) for addr in addresses]
        return characters

if __name__ == "__main__":
    app = App()
    app.mainloop()
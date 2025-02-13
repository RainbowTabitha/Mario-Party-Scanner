import customtkinter
import os
import sys
from PIL import Image, ImageTk
import tkinter as tk
import win32gui
import json
import functions
import dolphin_memory_engine
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigFileHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app

    def on_modified(self, event):
        if event.src_path.endswith("config.json"):
            print("config.json has been updated. Reloading...")
            self.app.load_name_overrides()

class App(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.load_name_overrides()

        self.valid_scene_ids = [
            {"89", "90", "91", "92", "93", "94"},
            {"118", "120", "122", "124", "126", "128", "130"},
            {"123", "124", "125", "126", "127", "128"},
            {"122", "123", "124", "125", "126", "127"},
            {"16", "17", "18", "19", "20", "21"}
        ]
        self.initial_load_done = False
        self.coin_image = None
        self.star_image = None
        self.mg_star_image = None
        self.coinStar_image = None
        self.happening_image = None
        self.running_image = None
        self.red_image = None
        self.shopping_image = None

        self.last_turn_zero_change_time = None
        self.delay_duration = 3500

        try:
            os.mkdir("data")
        except:
            pass

        self.title("Mario Party Scanner")
 

        self.ensure_config_exists()
        self.load_name_overrides()
        customtkinter.set_appearance_mode("Dark")

        self.geometry(f"{self.window_width - 30}x{self.window_height + 75}")

        self.home_frame = customtkinter.CTkFrame(self, corner_radius=12, fg_color=(self.bg_color, self.bg_color), width=self.window_width / 2, height=self.window_height / 2)
        self.home_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.turn_label = customtkinter.CTkLabel(self.home_frame, text="", font=("Helvetica", self.turn_label_size, "bold"))
        self.turn_label.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Configure grid columns to be evenly spaced
        for i in range(4):
            self.home_frame.grid_columnconfigure(i, weight=1)

        # Image labels and character name labels
        self.image_labels = []
        self.name_labels = []
        self.coin_labels = []
        self.star_labels = []
        self.mg_star_labels = []
        self.coin_star_labels = []
        self.happening_star_labels = []
        self.running_star_labels = []
        self.red_star_labels = []
        self.shopping_star_labels = []

        for i in range(4):
            self.load_name_overrides()
            img_label = customtkinter.CTkLabel(self.home_frame, text="", width=150, height=self.player_icon_size + 5, corner_radius=8)
            img_label.grid(row=1, column=i, padx=10, pady=5, sticky="nsew")
            self.image_labels.append(img_label)

            name_label = customtkinter.CTkLabel(self.home_frame, text="", font=("Helvetica", 24))
            name_label.grid(row=2, column=i, padx=10, pady=5, sticky="nsew")
            self.name_labels.append(name_label)

            star_label = customtkinter.CTkLabel(self.home_frame, text="", font=("Helvetica", self.stats_label_size))
            star_label.grid(row=3, column=i, padx=10, pady=(5, 2), sticky="nsew")
            self.star_labels.append(star_label)

            coin_label = customtkinter.CTkLabel(self.home_frame, text="", font=("Helvetica", self.stats_label_size))
            coin_label.grid(row=4, column=i, padx=10, pady=(2, 5), sticky="nsew")
            self.coin_labels.append(coin_label)

            coin_star_label = customtkinter.CTkLabel(self.home_frame, text="", font=("Helvetica", self.stats_label_size))
            coin_star_label.grid(row=6, column=i, padx=10, pady=(2, 5), sticky="nsew")
            self.coin_star_labels.append(coin_star_label)

            mg_star_label = customtkinter.CTkLabel(self.home_frame, text="", font=("Helvetica", self.stats_label_size))
            mg_star_label.grid(row=5, column=i, padx=10, pady=(5, 2), sticky="nsew")
            self.mg_star_labels.append(mg_star_label)

            happening_star_label = customtkinter.CTkLabel(self.home_frame, text="", font=("Helvetica", self.stats_label_size)) 
            happening_star_label.grid(row=7, column=i, padx=10, pady=(2, 5), sticky="nsew")
            self.happening_star_labels.append(happening_star_label)

            running_star_label = customtkinter.CTkLabel(self.home_frame, text="", font=("Helvetica", self.stats_label_size))
            running_star_label.grid(row=8, column=i, padx=10, pady=(2, 5), sticky="nsew")
            self.running_star_labels.append(running_star_label)

            red_star_label = customtkinter.CTkLabel(self.home_frame, text="", font=("Helvetica", self.stats_label_size))
            red_star_label.grid(row=9, column=i, padx=10, pady=(2, 5), sticky="nsew")
            self.red_star_labels.append(red_star_label)

            shopping_star_label = customtkinter.CTkLabel(self.home_frame, text="", font=("Helvetica", self.stats_label_size))
            shopping_star_label.grid(row=10, column=i, padx=10, pady=(2, 5), sticky="nsew")
            self.shopping_star_labels.append(shopping_star_label)

        self.cached_turn = None
        self.cached_final_turn = None

        self.update_turn_label()
        self.update_coins_and_stars()

        # Start file monitoring
        self.start_file_monitoring()

    def load_coin_image(self, game_id):
        if game_id == "GMPE01" or game_id == "GMPEDX":
            coin_image_path = functions.resource_path("assets/mp4/coins.png")
        elif game_id == "GP5E01":
            coin_image_path = functions.resource_path("assets/mp5/coins.png")
        elif game_id == "GP6E01":
            coin_image_path = functions.resource_path("assets/mp6/coins.png")
        elif game_id == "GP7E01":
            coin_image_path = functions.resource_path("assets/mp7/coins.png")
        elif game_id == "RM8E01":
            coin_image_path = functions.resource_path("assets/mp8/coins.png")
        try:
            if os.path.exists(coin_image_path):
                coin_image = Image.open(coin_image_path)
                coin_image = coin_image.resize((self.stats_label_size + 2, self.stats_label_size + 2), Image.LANCZOS)
                return ImageTk.PhotoImage(coin_image)
        except:
            pass
        return None

    def load_star_image(self, game_id):
        if game_id == "GMPE01" or game_id == "GMPEDX":
            coin_image_path = functions.resource_path("assets/mp4/stars.png")
        elif game_id == "GP5E01":
            coin_image_path = functions.resource_path("assets/mp5/stars.png")
        elif game_id == "GP6E01":
            coin_image_path = functions.resource_path("assets/mp6/stars.png")
        elif game_id == "GP7E01":
            coin_image_path = functions.resource_path("assets/mp7/stars.png")
        elif game_id == "RM8E01":
            coin_image_path = functions.resource_path("assets/mp8/stars.png")
        try:
            if os.path.exists(coin_image_path):
                coin_image = Image.open(coin_image_path)
                coin_image = coin_image.resize((self.stats_label_size + 2, self.stats_label_size + 2), Image.LANCZOS)
                return ImageTk.PhotoImage(coin_image)
        except:
            pass
        return None

    def load_happening_image(self, game_id):
        if game_id == "GMPE01" or game_id == "GMPEDX":
            coin_image_path = functions.resource_path("assets/mp4/happening.png")
        elif game_id == "GP5E01":
            coin_image_path = functions.resource_path("assets/mp5/happening.png")
        elif game_id == "GP6E01":
            coin_image_path = functions.resource_path("assets/mp6/happening.png")
        elif game_id == "GP7E01":
            coin_image_path = functions.resource_path("assets/mp7/happening.png")
        elif game_id == "RM8E01":
            coin_image_path = functions.resource_path("assets/mp8/happening.png")
        try:
            if os.path.exists(coin_image_path):
                coin_image = Image.open(coin_image_path)
                coin_image = coin_image.resize((self.stats_label_size + 2, self.stats_label_size + 2), Image.LANCZOS)
                return ImageTk.PhotoImage(coin_image)
        except:
            pass
        return None

    def load_minigame_image(self, game_id):
        if game_id == "GMPE01" or game_id == "GMPEDX":
            coin_image_path = functions.resource_path("assets/mp4/minigame.png")
        elif game_id == "GP5E01":
            coin_image_path = functions.resource_path("assets/mp5/minigame.png")
        elif game_id == "GP6E01":
            coin_image_path = functions.resource_path("assets/mp6/minigame.png")
        elif game_id == "GP7E01":
            coin_image_path = functions.resource_path("assets/mp7/minigame.png")
        elif game_id == "RM8E01":
            coin_image_path = functions.resource_path("assets/mp8/minigame.png")
        try:
            if os.path.exists(coin_image_path):
                coin_image = Image.open(coin_image_path)
                coin_image = coin_image.resize((self.stats_label_size + 2, self.stats_label_size + 2), Image.LANCZOS)
                return ImageTk.PhotoImage(coin_image)
        except:
            pass
        return None

    def load_coin_star_image(self, game_id):
        if game_id == "GMPE01" or game_id == "GMPEDX":
            coin_image_path = functions.resource_path("assets/mp4/coins.png")
        elif game_id == "GP5E01":
            coin_image_path = functions.resource_path("assets/mp5/coins.png")
        elif game_id == "GP6E01":
            coin_image_path = functions.resource_path("assets/mp6/item.png")
        elif game_id == "GP7E01":
            coin_image_path = functions.resource_path("assets/mp7/item.png")
        elif game_id == "RM8E01":
            coin_image_path = functions.resource_path("assets/mp8/item.png")
        try:
            if os.path.exists(coin_image_path):
                coin_image = Image.open(coin_image_path)
                coin_image = coin_image.resize((self.stats_label_size + 2, self.stats_label_size + 2), Image.LANCZOS)
                return ImageTk.PhotoImage(coin_image)
        except:
            pass
        return None

    def load_running_star_image(self, game_id):
        if game_id == "GP7E01":
            coin_image_path = functions.resource_path("assets/mp7/running.png")
        elif game_id == "RM8E01":
            coin_image_path = functions.resource_path("assets/mp8/running.png")
        try:
            if os.path.exists(coin_image_path):
                coin_image = Image.open(coin_image_path)
                coin_image = coin_image.resize((self.stats_label_size + 2, self.stats_label_size + 2), Image.LANCZOS)
                return ImageTk.PhotoImage(coin_image)
        except:
            pass
        return None

    def load_red_star_image(self, game_id):
        if game_id == "GP7E01":
            coin_image_path = functions.resource_path("assets/mp7/redspace.png")
        elif game_id == "RM8E01":
            coin_image_path = functions.resource_path("assets/mp8/redspace.png")
        try:
            if os.path.exists(coin_image_path):
                coin_image = Image.open(coin_image_path)
                coin_image = coin_image.resize((self.stats_label_size + 2, self.stats_label_size + 2), Image.LANCZOS)
                return ImageTk.PhotoImage(coin_image)
        except:
            pass
        return None

    def load_shopping_star_image(self, game_id):
        if game_id == "GP7E01":
            coin_image_path = functions.resource_path("assets/mp7/shopping.png")
        elif game_id == "RM8E01":
            coin_image_path = functions.resource_path("assets/mp8/shopping.png")
        try:
            if os.path.exists(coin_image_path):
                coin_image = Image.open(coin_image_path)
                coin_image = coin_image.resize((self.stats_label_size + 2, self.stats_label_size + 2), Image.LANCZOS)
                return ImageTk.PhotoImage(coin_image)
        except:
            pass
        return None

    def update_coins_and_stars(self):
        game_id = self.check_game_id()
        scene_id = self.get_scene_id(game_id)
        if scene_id in [id for valid_ids in self.valid_scene_ids for id in valid_ids]:
            if game_id:
                if not self.coin_image:
                    self.coin_image = self.load_coin_image(game_id)
                if not self.star_image:
                    self.star_image = self.load_star_image(game_id)
                if not self.mg_star_image:
                    self.mg_star_image = self.load_minigame_image(game_id)
                if not self.coinStar_image:
                    self.coinStar_image = self.load_coin_star_image(game_id)
                if not self.happening_image:
                    self.happening_image = self.load_happening_image(game_id)
                if not self.running_image:
                    self.running_image = self.load_running_star_image(game_id)
                if not self.shopping_image:
                    self.shopping_image = self.load_shopping_star_image(game_id)
                if not self.red_image:
                    self.red_image = self.load_red_star_image(game_id)

                for i in range(4):
                    player_stars = self.get_player_stars(game_id, i)
                    player_coins = self.get_player_coins(game_id, i)
                
                    if game_id != "RM8E01":
                        player_mg = self.get_player_mg(game_id, i)
                        player_coinStar = self.get_player_coinStar(game_id, i)
                        player_happening = self.get_player_happening(game_id, i)
                    
                    if game_id == "GP7E01" or game_id == "RM8E01":
                        player_runnning = self.get_player_running(game_id, i)
                        player_shopping = self.get_player_shopping(game_id, i)
                        player_red = self.get_player_red(game_id, i)

                    # Update coin label
                    self.coin_labels[i].configure(image=self.coin_image, compound='left', pady=10, text=f" {player_coins}")
                    self.coin_labels[i].image = self.coin_image

                    # Update star label
                    self.star_labels[i].configure(image=self.star_image, compound='left', pady=10, text=f" {player_stars}")
                    self.star_labels[i].image = self.star_image

                    # Update MG star label
                    self.mg_star_labels[i].configure(image=self.mg_star_image, compound='left', pady=10, text=f" {player_mg}")
                    self.mg_star_labels[i].image = self.star_image

                    # Update Coin star label
                    self.coin_star_labels[i].configure(image=self.coinStar_image, compound='left', pady=10, text=f" {player_coinStar}")
                    self.coin_star_labels[i].image = self.coinStar_image

                    # Update Happening star label
                    self.happening_star_labels[i].configure(image=self.happening_image, compound='left', pady=10, text=f" {player_happening}")
                    self.happening_star_labels[i].image = self.happening_image

                    if game_id == "GP7E01" or game_id == "RM8E01":
                        # Update Running star label
                        self.running_star_labels[i].configure(image=self.running_image, compound='left', pady=10, text=f" {player_runnning}")
                        self.running_star_labels[i].image = self.running_image

                        # Update Shopping star label
                        self.shopping_star_labels[i].configure(image=self.shopping_image, compound='left', pady=10, text=f" {player_shopping}")
                        self.shopping_star_labels[i].image = self.shopping_image


                        # Update Red star label
                        self.red_star_labels[i].configure(image=self.red_image, compound='left', pady=10, text=f" {player_red}")
                        self.red_star_labels[i].image = self.red_image

        self.after(20, self.update_coins_and_stars)  # Refresh every 5 seconds

    def ensure_config_exists(self):
        """Create a default config.json file if it doesn't exist."""
        config_path = "config.json"
        if not os.path.exists(config_path):
            default_config = {
                "names": {
                    "mario": "",
                    "luigi": "",
                    "peach": "",
                    "yoshi": "",
                    "wario": "",
                    "dk": "",
                    "daisy": "",
                    "waluigi": "",
                    "boo": "",
                    "koopakid": "",
                    "toad": "",
                    "toadette": "",
                    "drybones": "",
                    "birdo": "",
                    "blooper": "",
                    "hammerbro": ""
                },
                "playerIconSize": 150,
                "statsLabelSize": 26,
                "turnLabelSize": 32,
                "bgColor": "#323232",
                "windowSize": {
                    "width": 800,
                    "height": 600
                }
            }
            try:
                with open(config_path, "w") as file:
                    json.dump(default_config, file, indent=4)
            except Exception as e:
                print(f"Error creating config.json: {e}")

    def load_name_overrides(self):
        self.name_overrides = {}
        try:
            with open("config.json", "r") as file:
                data = json.load(file)
                if not isinstance(data, dict) or "names" not in data:
                    print("config.json is not a valid JSON object or missing 'names' key.")
                    return
                self.name_overrides = data["names"]
                self.player_icon_size = int(data["playerIconSize"])
                self.stats_label_size = int(data["statsLabelSize"])
                self.turn_label_size = int(data["turnLabelSize"])
                self.bg_color = data["bgColor"]
                window_size = data["windowSize"]
                self.window_width = window_size["width"]
                self.window_height = window_size["height"]
        except FileNotFoundError:
            print("config.json file not found.")
        except json.JSONDecodeError:
            print("Error decoding config.json.")
        except KeyError as e:
            print(f"Missing key in config.json: {e}")

    def start_file_monitoring(self):
        event_handler = ConfigFileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(os.path.abspath("config.json")), recursive=False)
        observer.start()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
       # Stop the observer if it exists
       if hasattr(self, 'observer'):
           self.observer.stop()
           self.observer.join()
       self.destroy()

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
            os.environ["DME_DOLPHIN_PROCESS_NAME"] = "Dolphin-MPN"
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
            "GMPEDX": (0x8018FCFC, ["89", "90", "91", "92", "93", "94"]),
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

    def get_player_stars(self, game_id, player_index):
        address_map = {
            "GMPE01": [0x8018FC62, 0x8018FC92, 0x8018FCC2, 0x8018FCF2],
            "GMPEDX": [0x8018FC62, 0x8018FC92, 0x8018FCC2, 0x8018FCF2],
            "GP5E01": [0x8022A0A4, 0x8022A1AC, 0x8022A2B4, 0x8022A3BC],
            "GP6E01": [0x80265780, 0x80265888, 0x80265990, 0x80265A98],
            "GP7E01": [0x80290CD0, 0x80290DE0, 0x80290EF0, 0x80291000],
            "RM8E01": [0x80228390, 0x802283A9, 0x802283B3, 0x802283BD]
        }
        
        if game_id in address_map:
            try:
                address = address_map[game_id][player_index]
                score_bytes = dolphin_memory_engine.read_bytes(address, 2)
                score = int.from_bytes(score_bytes, byteorder='big')
                return str(score)
            except:
                return "0"
        return "0"

    def get_player_coins(self, game_id, player_index):
        address_map = {
            "GMPE01": [0x8018FC54, 0x8018FC84, 0x8018FCB4, 0x8018FCE4],
            "GMPEDX": [0x8018FC54, 0x8018FC84, 0x8018FCB4, 0x8018FCE4],
            "GP5E01": [0x8022A090, 0x8022A198, 0x8022A2A0, 0x8022A3A8],
            "GP6E01": [0x8026576C, 0x80265874, 0x8026597C, 0x80265A84],
            "GP7E01": [0x80290CBE, 0x80290DCE, 0x80290EDE, 0x80290FEE],
            "RM8E01": [0x8022831E, 0x80228436, 0x8022854E, 0x80228666]
        }
        
        if game_id in address_map:
            try:
                address = address_map[game_id][player_index]
                coins_bytes = dolphin_memory_engine.read_bytes(address, 2)
                coins = int.from_bytes(coins_bytes, byteorder='big')
                return str(coins)
            except:
                return "0"
        return "0"

    def get_player_mg(self, game_id, player_index):
        address_map = {
            "GMPE01": [0x8018FC56, 0x8018FC86, 0x8018FCB6, 0x8018FCE6],
            "GMPEDX": [0x8018FC56, 0x8018FC86, 0x8018FCB6, 0x8018FCE6],
            "GP5E01": [0x8022A092, 0x8022A19A, 0x8022A2A2, 0x8022A3AA],
            "GP6E01": [0x8026576E, 0x80265876, 0x8026597E, 0x80265A86],
            "GP7E01": [0x80290CC0, 0x80290DD0, 0x80290EE0, 0x80290FF0]
        }
        
        if game_id in address_map:
            try:
                address = address_map[game_id][player_index]
                coins_bytes = dolphin_memory_engine.read_bytes(address, 2)
                coins = int.from_bytes(coins_bytes, byteorder='big')
                return str(coins)
            except:
                return "0"
        return "0"


    def get_player_coinStar(self, game_id, player_index):
        address_map = {
            "GMPE01": [0x8018FC5A, 0x8018FC8A, 0x8018FCBA, 0x8018FCEA],
            "GMPEDX": [0x8018FC5A, 0x8018FC8A, 0x8018FCBA, 0x8018FCEA],
            "GP5E01": [0x8022A096, 0x8022A19E, 0x8022A2A6, 0x8022A3AE],
            "GP6E01": [0x80265784, 0x8026588C, 0x80265994, 0x80265A9C],
            "GP7E01": [0x80290CD4, 0x80290DE4, 0x80290EF4, 0x80291004]
        }
        
        if game_id in address_map:
            try:
                address = address_map[game_id][player_index]
                coins_bytes = dolphin_memory_engine.read_bytes(address, 2)
                coins = int.from_bytes(coins_bytes, byteorder='big')
                return str(coins)
            except:
                return "0"
        return "0"

    def get_player_happening(self, game_id, player_index):
        address_map = {
            "GMPE01": [0x8018FC4E, 0x8018FC7E, 0x8018FCAE, 0x8018FCDE],
            "GMPEDX": [0x8018FC4E, 0x8018FC7E, 0x8018FCAE, 0x8018FCDE],
            "GP5E01": [0x8022A087, 0x8022A18F, 0x8022A297, 0x8022A39F], 
            "GP6E01": [0x80265767, 0x8026586E, 0x80265977, 0x80265A7E],
            "GP7E01": [0x80290CB7, 0x80290DC7, 0x80290ED7, 0x80290FE7]
        }
        
        if game_id in address_map:
            try:
                address = address_map[game_id][player_index]
                coins_bytes = dolphin_memory_engine.read_bytes(address, 1)
                coins = int.from_bytes(coins_bytes, byteorder='big')
                return str(coins)
            except:
                return "0"
        return "0"

    def get_player_running(self, game_id, player_index):
        address_map = {
            "GP7E01": [0x80290CB0, 0x80290DC0, 0x80290ED0, 0x80290FE0]
        }
        
        if game_id in address_map:
            try:
                address = address_map[game_id][player_index]
                coins_bytes = dolphin_memory_engine.read_bytes(address, 2)
                coins = int.from_bytes(coins_bytes, byteorder='big')
                return str(coins)
            except:
                return "0"
        return "0"

    def get_player_shopping(self, game_id, player_index):
        address_map = {
            "GP7E01": [0x80290CD6, 0x80290DE6, 0x80290EF6, 0x80291006]
        }
        
        if game_id in address_map:
            try:
                address = address_map[game_id][player_index]
                coins_bytes = dolphin_memory_engine.read_bytes(address, 2)
                coins = int.from_bytes(coins_bytes, byteorder='big')
                return str(coins)
            except:
                return "0"
        return "0"

    def get_player_red(self, game_id, player_index):
        address_map = {
            "GP7E01": [0x80290CB5, 0x80290DC5, 0x80290ED5, 0x80290FE5]
        }
        
        if game_id in address_map:
            try:
                address = address_map[game_id][player_index]
                coins_bytes = dolphin_memory_engine.read_bytes(address, 1)
                coins = int.from_bytes(coins_bytes, byteorder='big')
                return str(coins)
            except:
                return "0"
        return "0"

    def get_final_turn(self, game_id):
        scene_id = self.get_scene_id(game_id)
        address_map = {
            "GMPE01": (0x8018FCFD, ["89", "90", "91", "92", "93", "94"]),
            "GMPEDX": (0x8018FCFD, ["89", "90", "91", "92", "93", "94"]),
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
            "GMPEDX": 0x801D3CE3,
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
            scene_id = self.get_scene_id(game_id)

            if not self.initial_load_done:
                if scene_id in [id for valid_ids in self.valid_scene_ids for id in valid_ids]:
                    self.initial_load_done = True
                else:
                    self.turn_label.configure(text="Scene not valid")
                    # Hide portraits and names if scene ID is not valid
                    for img_label, name_label in zip(self.image_labels, self.name_labels):
                        img_label.grid_forget()
                        name_label.grid_forget()

            if self.initial_load_done:
                if current_turn == "255" and self.cached_turn != "255":
                    current_turn = self.cached_turn

                if current_turn == "0" and self.cached_turn != "0":
                    self.cached_turn = current_turn
                    self.last_turn_zero_change_time = self.after(self.delay_duration, self.update_coins_and_stars)
                
                if current_turn != "0":
                    self.cached_turn = current_turn

                if final_turn is None:
                    final_turn = self.cached_final_turn

                if current_turn and final_turn:
                    self.cached_final_turn = final_turn

                    self.turn_label.configure(text=f"Turn: {current_turn} / {final_turn}")
                    self.write_turn_to_file(current_turn, final_turn)
                    self.update_images(game_id)

                    if current_turn == "0":
                        for img_label, name_label in zip(self.image_labels, self.name_labels):
                            img_label.grid_forget()
                            name_label.grid_forget()
                    else:
                        for i, (img_label, name_label) in enumerate(zip(self.image_labels, self.name_labels)):
                            img_label.grid(row=1, column=i, padx=10, pady=1, sticky="nsew")
                            name_label.grid(row=2, column=i, padx=10, pady=5, sticky="nsew")

                            try:
                                name_label.configure(text=f"{self.get_character_name(self.get_character_id(game_id)[i], i)}")
                            except:
                                pass
        

                else:
                    self.turn_label.configure(text="Not detected")
                    for img_label, name_label in zip(self.image_labels, self.name_labels):
                        img_label.grid_forget()
                        name_label.grid_forget()

            else:
                self.turn_label.configure(text="Not detected")
                for img_label, name_label in zip(self.image_labels, self.name_labels):
                    img_label.grid_forget()
                    name_label.grid_forget()

        else:
            self.turn_label.configure(text="Not detected")
            for img_label, name_label in zip(self.image_labels, self.name_labels):
                img_label.grid_forget()
                name_label.grid_forget()

        self.after(20, self.update_turn_label)

    def write_turn_to_file(self, current_turn, final_turn):
        with open("data/turn.txt", "w") as f:
            f.write(f"Turn: {current_turn} / {final_turn}\n")

    def update_images(self, game_id):
        # Retrieve character IDs
        character_ids = self.get_character_id(game_id)

        # Generate image paths based on character IDs
        if game_id == "GMPE01" or game_id == "GMPEDX":
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
            try:
                if i < len(image_paths):
                    image_path = image_paths[i]

                    # Load and display image
                    if image_path and os.path.exists(image_path):
                        image = Image.open(image_path)
                        image = image.resize((self.player_icon_size, self.player_icon_size), Image.LANCZOS)
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
            except:
                pass

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

        # Check if there is an override for this character ID
        override_name = self.name_overrides.get(character_id, "").strip()

        # Use the override name if it's not empty; otherwise, use the default name
        return override_name if override_name else default_name

    def get_character_id(self, game_id):
        address_map = {
            "GMPE01": [0x8018FC11, 0x8018FC1B, 0x8018FC25, 0x8018FC2F],
            "GMPEDX": [0x8018FC11, 0x8018FC1B, 0x8018FC25, 0x8018FC2F],
            "GP5E01": [0x8022A049, 0x8022A053, 0x8022A05D, 0x8022A067],
            "GP6E01": [0x80265729, 0x80265733, 0x8026573D, 0x80265747],
            "GP7E01": [0x80290C49, 0x80290C53, 0x80290C5D, 0x80290C67],
            "RM8E01": [0x802282D1, 0x802282DB, 0x802282E5, 0x802282EF]
        }

        if game_id == "GMPE01" or game_id == "GMPEDX":
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
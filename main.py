import os
import sys
import json
import logging
import pygame
import unittest
import random
from config import *
from engine import loc, theme_mgr, ObjectManager, measure_time
from entities import ProceduralWave
from states import MenuState, GameState, PlayingState, RhythmSelectionState, ShopState, SettingsState, GameOverState

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("game_log.log"), logging.StreamHandler()])
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

class Game:
    def __init__(self, headless=False):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        if not pygame.get_init(): pygame.init()
        self._window = pygame.Surface((WIDTH, HEIGHT)) if headless else pygame.display.set_mode((WIDTH, HEIGHT))
        if not headless: pygame.display.set_caption("Retinal")
            
        self._clock = pygame.time.Clock(); self._running = True
        self._settings = {"star_rate": 100, "star_rate_name": "Normal"}; self.sfx_volume = 0.5
        self.data = { "high_score": 0, "currency": 0, "inventory": ["Default", "Star", "Default_Size"], "equipped": {"color": "Default", "shape": "Star", "size": 0} }
        self.notes_data = {}; self.sound_bank = {}

        self._load_data(); self._load_notes()
        if self.data["currency"] < 10000: self.data["currency"] = 1000000; self._save_data()

        self._load_fonts(); self._create_background()
        self._menu_music_path = os.path.join(SOUND_FOLDER, "menu_sound.mp3")
        self._game_music_path = os.path.join(SOUND_FOLDER, "game_sound.mp3")
        self._sound_effect_paths = {"hight": os.path.join(SOUND_FOLDER, "hight.mp3")}
        
        self._current_music_path = None; self._catch_sound = None; self._sound_channel_star = None
        
        if not headless:
            self._load_audio(); self._load_all_note_sounds()
            self._current_state = MenuState(self); self.play_music(self._menu_music_path, volume=0.5)
        else: self._current_state = None 

    def _load_data(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    loaded_data = json.load(f)
                    for key in self.data:
                        if key in loaded_data: self.data[key] = loaded_data[key]
            except Exception as e: logging.error(f"Error loading save file: {e}")

    def _load_notes(self):
        try:
            with open(NOTES_FILE, 'r') as f: self.notes_data = json.load(f)
        except Exception: self.notes_data = {}

    def _save_data(self):
        try:
            with open(SAVE_FILE, 'w') as f: json.dump(self.data, f)
        except Exception as e: logging.error(f"Error saving data: {e}")

    def update_high_score(self, score):
        if score > self.data["high_score"]: self.data["high_score"] = score; self._save_data()
    def get_high_score(self): return self.data["high_score"]
    def get_currency(self): return self.data["currency"]
    def add_currency(self, amount): self.data["currency"] += amount; self._save_data()
    def has_item(self, category, item_id): return True if item_id in ["Default", "Star", 0] else item_id in self.data["inventory"]
    def buy_item(self, category, item_id, price):
        if self.data["currency"] >= price:
            self.data["currency"] -= price; self.data["inventory"].append(item_id); self._save_data(); return True
        return False
    def equip_item(self, category, item_id): self.data["equipped"][category] = item_id; self._save_data()
    def is_equipped(self, category, item_id): return self.data["equipped"].get(category) == item_id
    def get_equipped(self, category): return self.data["equipped"].get(category)

    def _load_fonts(self):
        target_font = FONT_FILE_UA if loc.current_lang == "UA" else FONT_FILE_EN
        s_big, s_med, s_small, s_tiny = (50, 30, 20, 16) if loc.current_lang == "UA" else (70, 40, 30, 24)
        try:
            self.FONT_BIG = pygame.font.Font(target_font, s_big)
            self.FONT_MEDIUM = pygame.font.Font(target_font, s_med)
            self.FONT_SMALL = pygame.font.Font(target_font, s_small)
            self.FONT_TINY = pygame.font.Font(target_font, s_tiny)
        except Exception:
            self.FONT_BIG = pygame.font.SysFont("Arial", s_big, bold=True)
            self.FONT_MEDIUM = pygame.font.SysFont("Arial", s_med)
            self.FONT_SMALL = pygame.font.SysFont("Arial", s_small)
            self.FONT_TINY = pygame.font.SysFont("Arial", s_tiny)

    def _create_background(self):
        self._waves_manager = ObjectManager[ProceduralWave]()
        for i in range(len(theme_mgr.themes["light"]["bg_elements"])): self._waves_manager.add(ProceduralWave(i))
        self._bg_stars = [{'pos': (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 'radius': random.randint(1, 2)} for _ in range(NUM_BG_STARS)]

    def _load_audio(self):
        try:
            hight_path = self._sound_effect_paths.get("hight")
            if hight_path and os.path.exists(hight_path):
                 self._catch_sound = pygame.mixer.Sound(hight_path); self._sound_channel_star = pygame.mixer.Channel(0)
            else: self._catch_sound = None; self._sound_channel_star = None
        except: self._catch_sound = None; self._sound_channel_star = None

    @measure_time
    def _load_all_note_sounds(self):
        if not os.path.exists(SOUND_FOLDER): return
        for filename in os.listdir(SOUND_FOLDER):
            if filename.endswith(".ogg"):
                note_name = os.path.splitext(filename)[0]
                try:
                    sound = pygame.mixer.Sound(os.path.join(SOUND_FOLDER, filename))
                    self.sound_bank[note_name] = sound
                    if '-' in note_name: self.sound_bank[note_name.replace('-', '#')] = sound
                except Exception: pass

    def play_note_sound(self, note_name):
        sound = self.sound_bank.get(note_name)
        if sound: sound.set_volume(self.sfx_volume); sound.play()

    def play_catch_sound(self):
        if self._sound_channel_star and self._catch_sound: self._catch_sound.set_volume(self.sfx_volume); self._sound_channel_star.play(self._catch_sound)

    def play_music(self, music_path: str, fade_ms: int = 1000, volume: float = 0.5):
        if not os.path.exists(music_path): self._current_music_path = None; return
        if music_path == self._current_music_path and pygame.mixer.music.get_busy(): pygame.mixer.music.set_volume(volume); return
        if pygame.mixer.music.get_busy(): pygame.mixer.music.fadeout(fade_ms)
        try:
            pygame.mixer.music.load(music_path); pygame.mixer.music.set_volume(volume); pygame.mixer.music.play(-1, fade_ms=fade_ms)
            self._current_music_path = music_path
        except: self._current_music_path = None

    def run(self):
        while self._running:
            dt = self._clock.tick(FPS) / 1000.0
            switched = theme_mgr.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.stop()
                self._current_state.handle_event(event)
            self._waves_manager.update_all(dt, theme_switched=switched)
            self._current_state.update(dt)
            self._window.fill(theme_mgr.get("bg_color"))
            if theme_mgr.get("has_bg_stars"):
                for star in self._bg_stars: pygame.draw.circle(self._window, WHITE, star['pos'], star['radius'])
            self._waves_manager.draw_all(self._window)
            self._current_state.draw(self._window)
            theme_mgr.draw_transition(self._window)
            pygame.display.flip()
        pygame.quit()

    def change_state(self, new_state: GameState):
        self._current_state = new_state
        if isinstance(new_state, (MenuState, SettingsState, GameOverState, RhythmSelectionState, ShopState)): self.play_music(self._menu_music_path, volume=pygame.mixer.music.get_volume())
        elif isinstance(new_state, PlayingState): self.play_music(self._game_music_path, volume=0.3)

    def stop(self): self._running = False
    def get_settings(self) -> dict: return self._settings

class TestRetinalSystems(unittest.TestCase):
    def setUp(self): self.game = Game(headless=True); loc.current_lang = "EN"
    def test_localization_defaults(self): self.assertEqual(loc.current_lang, "EN"); self.assertEqual(loc.get("START"), "START")
    def test_localization_toggle(self):
        loc.toggle_lang(); self.assertEqual(loc.current_lang, "UA"); self.assertEqual(loc.get("START"), "ГРАТИ")
        loc.toggle_lang(); self.assertEqual(loc.current_lang, "EN")
    def test_theme_manager(self): theme_mgr.current_theme = "dark"; theme_mgr.start_transition(); self.assertTrue(theme_mgr.is_transitioning); self.assertEqual(theme_mgr.target_theme, "light")
    def test_economy_add_currency(self): initial = self.game.get_currency(); self.game.add_currency(500); self.assertEqual(self.game.get_currency(), initial + 500)
    def test_economy_buy_item_success(self):
        self.game.data["currency"] = 1000; result = self.game.buy_item("color", "TestBlue", 500)
        self.assertTrue(result); self.assertEqual(self.game.get_currency(), 500); self.assertTrue(self.game.has_item("color", "TestBlue"))
    def test_economy_buy_item_fail(self):
        self.game.data["currency"] = 10; result = self.game.buy_item("color", "ExpensiveGold", 500)
        self.assertFalse(result); self.assertEqual(self.game.get_currency(), 10); self.assertFalse(self.game.has_item("color", "ExpensiveGold"))
    def test_highscore_update(self):
        self.game.data["high_score"] = 100; self.game.update_high_score(50); self.assertEqual(self.game.get_high_score(), 100)
        self.game.update_high_score(200); self.assertEqual(self.game.get_high_score(), 200)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        sys.argv.pop(1); unittest.main()
    else: game = Game(); game.run()
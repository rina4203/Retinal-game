import os

# --- FILE PATHS ---
SOUND_FOLDER = "sound"
FONT_FOLDER = "etc"
HIGHSCORE_FILE = "highscore.txt"
SAVE_FILE = "save_data.json"
NOTES_FILE = os.path.join(SOUND_FOLDER, "notes.json")
FONT_FILE_EN = os.path.join(FONT_FOLDER, "font.otf")
FONT_FILE_UA = os.path.join(FONT_FOLDER, "FiorinaTitle-Light.otf")

# --- SONG CONFIGURATION ---
SONG_LIST = [
    { "name": "Twinkle Twinkle",     "bpm": 100, "note_id": "1" },
    { "name": "Happy Birthday",      "bpm": 110, "note_id": "2" },
    { "name": "Birds of a Feather",  "bpm": 120, "note_id": "3" },
    { "name": "Rolling in the Deep", "bpm": 125, "note_id": "4" }
]

# --- CONSTANTS ---
WIDTH, HEIGHT = 500, 800
FPS = 60
MAX_PLATFORM_SPEED = 14
NUM_BG_STARS = 200
MAX_MISSED_STARS = 10
LANE_WIDTH = WIDTH // 3
LANE_CENTERS = [LANE_WIDTH * 0.5, LANE_WIDTH * 1.5, LANE_WIDTH * 2.5]

# --- COLORS ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED_ERROR = (215, 80, 80)
GOLD = (240, 200, 80)
GREEN_BUY = (100, 200, 120)
PASTEL_CREAM = (255, 253, 208)
BOHO_BG = (135, 206, 250)

SHOP_COLORS = {
    "Default": None, "Red": (230, 100, 100), "Orange": (240, 160, 100),
    "Yellow": (240, 220, 100), "Green": (120, 180, 120), "Cyan": (100, 200, 200),
    "Blue": (100, 140, 200), "Purple": (160, 120, 200), "Pink": (230, 150, 180)
}
# settings.py
import pygame

# Window
WIDTH, HEIGHT = 480, 640
FPS = 60
TITLE = "Crossy Road (2D) - Clone"

# Grid / tiles
TILE = 40
COLS = WIDTH // TILE            # 12
ROWS = HEIGHT // TILE           # 16
CAMERA_MARGIN_TILES = 6         # keep player at least this many tiles above bottom when moving up

# Gameplay
MOVE_COOLDOWN = 0.08            # seconds; prevents super-fast key repeats
MAX_GEN_AHEAD = 40              # generate lanes up to this many tiles ahead of camera top

# Colors
COLOR_BG = (25, 25, 28)
COLOR_TEXT = (235, 235, 235)

LANE_COLORS = {
    "grass": (60, 140, 70),
    "road":  (55, 55, 60),
    "water": (35, 95, 150),
    "rail":  (70, 55, 45),
}

# Entity colors
COLOR_PLAYER = (245, 220, 90)
COLOR_CAR = (220, 80, 80)
COLOR_LOG = (150, 110, 60)
COLOR_TRAIN = (220, 220, 220)
COLOR_TREE = (30, 90, 35)

# Fonts
def make_font(size: int) -> pygame.font.Font:
    return pygame.font.SysFont(None, size)

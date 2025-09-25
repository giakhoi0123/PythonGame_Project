"""
Cấu hình và hằng số cho Pacman Nova.
Tách riêng để dễ chỉnh sửa tham số gameplay và UI.
"""

from dataclasses import dataclass

# --- Visual ---
TILE_SIZE: int = 24
GRID_OUTLINE: int = 2

# Màu (R, G, B)
COLOR_BG = (12, 12, 22)
COLOR_WALL = (30, 60, 160)
COLOR_PELLET = (245, 235, 120)
COLOR_POWER = (255, 180, 80)
COLOR_TEXT = (230, 230, 230)
COLOR_UI_PANEL = (25, 25, 40)
COLOR_UI_ACCENT = (90, 190, 255)
COLOR_HEALTH_GOOD = (70, 220, 100)
COLOR_HEALTH_WARN = (230, 160, 70)
COLOR_HEALTH_LOW = (230, 60, 60)
COLOR_P1 = (255, 215, 0)
COLOR_P2 = (255, 105, 180)
COLOR_GHOST = (250, 90, 90)
COLOR_BOSS = (180, 60, 220)
COLOR_SHIELD = (70, 200, 255)
COLOR_SPEED = (120, 255, 120)

HUD_HEIGHT = 80

# --- Gameplay ---
BASE_PLAYER_SPEED: float = 4.0  # tiles / s
PLAYER_ACCEL: float = 22.0      # pixels / s^2
PLAYER_MAX_HEALTH: int = 5

SPEED_BOOST_MULT: float = 1.75
SPEED_BOOST_DURATION: float = 2.2
SPEED_BOOST_COOLDOWN: float = 7.0

INVIS_DURATION: float = 3.5
INVIS_COOLDOWN: float = 10.0

DASH_DISTANCE_TILES: float = 2.0
DASH_COOLDOWN: float = 6.0

MAGNET_BASE_RADIUS_TILES: float = 2.0
MAGNET_PULSE_RADIUS_TILES: float = 4.0
MAGNET_PULSE_COOLDOWN: float = 8.0

SHIELD_DURATION: float = 4.0
SHIELD_COOLDOWN: float = 12.0

ITEM_SPAWN_INTERVAL: float = 8.0
ITEM_DESPAWN_TIME: float = 18.0

PELLET_SCORE: int = 10
ITEM_SCORE: int = 50
GHOST_SCORE: int = 200
BOSS_SCORE: int = 1000
POWER_FRIGHT_BONUS: int = 50

GHOST_BASE_SPEED: float = 3.2     # tiles / s
GHOST_SCATTER_TIME: float = 4.0
GHOST_CHASE_TIME: float = 12.0
GHOST_FRIGHT_TIME: float = 4.0

BOSS_SPEED: float = 3.6
BOSS_CHARGE_MULT: float = 2.6
BOSS_CHARGE_INTERVAL: float = 6.0
BOSS_HEALTH: int = 5

# Nâng cấp giữa màn
UPGRADES = [
    "Tăng tốc độ cơ bản",
    "Tăng máu tối đa",
    "Kéo dài tàng hình",
    "Tăng bán kính nam châm",
]

# --- Độ khó ---
@dataclass
class Difficulty:
    name: str
    ghost_speed_mult: float
    ghost_count: int
    boss_present: bool

DIFFICULTIES = [
    Difficulty("Easy", ghost_speed_mult=0.9, ghost_count=3, boss_present=False),
    Difficulty("Normal", ghost_speed_mult=1.0, ghost_count=4, boss_present=True),
    Difficulty("Hard", ghost_speed_mult=1.15, ghost_count=5, boss_present=True),
]

DEFAULT_VOLUME: float = 0.6
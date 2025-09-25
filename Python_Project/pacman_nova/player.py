"""
Người chơi: di chuyển lưới mượt, kỹ năng và nâng cấp.
P1: Tăng tốc (Right Shift), Tàng hình (Right Ctrl)
P2: Dash (Left Shift), Nam châm (Space)
"""

from __future__ import annotations

from typing import Tuple
import pygame
from settings import (
    TILE_SIZE, BASE_PLAYER_SPEED, PLAYER_ACCEL, PLAYER_MAX_HEALTH,
    SPEED_BOOST_MULT, SPEED_BOOST_DURATION, SPEED_BOOST_COOLDOWN,
    INVIS_DURATION, INVIS_COOLDOWN, DASH_DISTANCE_TILES, DASH_COOLDOWN,
    MAGNET_BASE_RADIUS_TILES, MAGNET_PULSE_RADIUS_TILES, MAGNET_PULSE_COOLDOWN,
    COLOR_P1, COLOR_P2, COLOR_SHIELD
)
from utils import Timer, clamp


class Player:
    def __init__(self, idx: int, spawn: Tuple[int, int], color):
        self.idx = idx  # 1 hoặc 2
        self.tx, self.ty = spawn
        self.x = self.tx * TILE_SIZE + TILE_SIZE / 2
        self.y = self.ty * TILE_SIZE + TILE_SIZE / 2
        self.vx = 0.0
        self.vy = 0.0
        self.dir = (0, 0)  # hướng mong muốn
        self.color = color
        self.speed_tiles = BASE_PLAYER_SPEED
        self.health_max = PLAYER_MAX_HEALTH
        self.health = self.health_max
        self.score = 0

        # Kỹ năng chung
        self.boost_timer = Timer(SPEED_BOOST_DURATION)
        self.boost_cd = Timer(SPEED_BOOST_COOLDOWN)
        self.invis_timer = Timer(INVIS_DURATION)
        self.invis_cd = Timer(INVIS_COOLDOWN)
        self.shield_timer = Timer(0.0)  # tắt khi 0

        # Kỹ năng riêng
        self.dash_cd = Timer(DASH_COOLDOWN)
        self.magnet_cd = Timer(MAGNET_PULSE_COOLDOWN)
        self.magnet_radius_tiles = MAGNET_BASE_RADIUS_TILES

        # Cờ do item
        self.place_trap = False
        self.trigger_bomb = False

        # Nâng cấp
        self.upg_speed_bonus = 0.0
        self.upg_invis_bonus = 0.0
        self.upg_extra_hp = 0

    def upgrade(self, name: str):
        if "Tăng tốc độ" in name:
            self.upg_speed_bonus += 0.3
        elif "Tăng máu tối đa" in name:
            self.upg_extra_hp += 1
            self.health_max += 1
            self.health = min(self.health_max, self.health + 1)
        elif "Kéo dài tàng hình" in name:
            self.upg_invis_bonus += 0.8
        elif "Tăng bán kính nam châm" in name:
            self.magnet_radius_tiles += 0.8

    def _speed_mult(self) -> float:
        mult = 1.0 + self.upg_speed_bonus
        if self.boost_timer.time_left > 0:
            mult *= SPEED_BOOST_MULT
        return mult

    def is_invisible(self) -> bool:
        return self.invis_timer.time_left > 0.0

    def has_shield(self) -> bool:
        return self.shield_timer.time_left > 0.0

    def pixel_center(self) -> Tuple[int, int]:
        return int(self.x), int(self.y)

    def hurt(self, dmg: int):
        if self.has_shield():
            return
        self.health = max(0, self.health - dmg)

    def heal(self, amt: int):
        self.health = min(self.health_max, self.health + amt)

    def activate_speed(self, mult: float, duration: float):
        self.boost_timer.set_and_start(duration)

    def activate_invisibility(self):
        if self.invis_cd.ready():
            self.invis_timer.set_and_start(INVIS_DURATION + self.upg_invis_bonus)
            self.invis_cd.set_and_start(INVIS_COOLDOWN)

    def activate_shield(self, duration: float):
        self.shield_timer.set_and_start(duration)

    def dash(self):
        if not self.dash_cd.ready():
            return
        dx, dy = self.dir
        if dx == dy == 0:
            return
        self.x += dx * DASH_DISTANCE_TILES * TILE_SIZE
        self.y += dy * DASH_DISTANCE_TILES * TILE_SIZE
        self.dash_cd.set_and_start(DASH_COOLDOWN)

    def magnet_pulse_radius(self) -> float:
        if self.magnet_cd.time_left <= MAGNET_PULSE_COOLDOWN - 0.2:
            return MAGNET_PULSE_RADIUS_TILES * TILE_SIZE
        return self.magnet_radius_tiles * TILE_SIZE

    def handle_input(self, pressed, is_p1: bool):
        if is_p1:
            dx = int(pressed[pygame.K_RIGHT]) - int(pressed[pygame.K_LEFT])
            dy = int(pressed[pygame.K_DOWN]) - int(pressed[pygame.K_UP])
            self.dir = (dx, dy) if abs(dx) + abs(dy) <= 1 else self.dir
        else:
            dx = int(pressed[pygame.K_d]) - int(pressed[pygame.K_a])
            dy = int(pressed[pygame.K_s]) - int(pressed[pygame.K_w])
            self.dir = (dx, dy) if abs(dx) + abs(dy) <= 1 else self.dir

    def handle_skills(self, pressed, is_p1: bool):
        if is_p1:
            if pressed[pygame.K_RSHIFT] and self.boost_cd.ready():
                self.boost_timer.start()
                self.boost_cd.start()
            if pressed[pygame.K_RCTRL]:
                self.activate_invisibility()
        else:
            if pressed[pygame.K_LSHIFT]:
                self.dash()
            if pressed[pygame.K_SPACE] and self.magnet_cd.ready():
                self.magnet_cd.start()  # phát xung nam châm ngắn
                # tác dụng thực hiện ở main khi hút pellet

    def update(self, dt: float, is_blocked):
        # cập nhật cooldown
        self.boost_timer.tick(dt)
        self.boost_cd.tick(dt)
        self.invis_timer.tick(dt)
        self.invis_cd.tick(dt)
        self.shield_timer.tick(dt)
        self.dash_cd.tick(dt)
        self.magnet_cd.tick(dt)

        # vận tốc mục tiêu theo hướng
        speed_px = (self.speed_tiles + self.upg_speed_bonus) * TILE_SIZE * self._speed_mult()
        target_vx = self.dir[0] * speed_px
        target_vy = self.dir[1] * speed_px

        # easing vận tốc
        self.vx = clamp(target_vx, -speed_px, speed_px)
        self.vy = clamp(target_vy, -speed_px, speed_px)

        nx = self.x + self.vx * dt
        ny = self.y + self.vy * dt

        # chặn theo tường bằng tile
        def blocked(px: float, py: float) -> bool:
            tx = int(px // TILE_SIZE)
            ty = int(py // TILE_SIZE)
            # co viền để dễ đi qua
            return is_blocked(tx, ty)

        # tách theo trục
        if not blocked(nx, self.y):
            self.x = nx
        if not blocked(self.x, ny):
            self.y = ny

    def draw(self, surf):
        cx, cy = self.pixel_center()
        r = TILE_SIZE // 2 - 2
        col = self.color
        if self.is_invisible():
            # vẽ nhạt hơn khi tàng hình
            body = (*col, 120)
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, body, (r, r), r)
            surf.blit(s, (cx - r, cy - r))
        else:
            pygame.draw.circle(surf, col, (cx, cy), r)

        if self.has_shield():
            s = pygame.Surface((r * 2 + 12, r * 2 + 12), pygame.SRCALPHA)
            pygame.draw.circle(s, (*COLOR_SHIELD, 120), (s.get_width() // 2, s.get_height() // 2), r + 6, 3)
            surf.blit(s, (cx - s.get_width() // 2, cy - s.get_height() // 2))
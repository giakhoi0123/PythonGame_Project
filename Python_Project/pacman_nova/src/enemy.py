"""
Kẻ địch: Ghost AI có phối hợp (bủa vây) và Boss có chiêu lao nhanh.
- Ghost chia vai: chặn đầu (intercept), ép hướng (herd), bám đuôi (chase).
- Dùng A* để tìm ô mục tiêu gần nhất theo vai trò.
"""

from __future__ import annotations

import random
from typing import List, Tuple, Optional
import pygame
from utils import a_star
from settings import TILE_SIZE, GHOST_BASE_SPEED, COLOR_GHOST, GHOST_FRIGHT_TIME, COLOR_BOSS, BOSS_SPEED, BOSS_CHARGE_INTERVAL, BOSS_CHARGE_MULT, BOSS_HEALTH


class Ghost:
    def __init__(self, idx: int, tile_pos: Tuple[int, int], speed_mult: float = 1.0):
        self.idx = idx
        self.tx, self.ty = tile_pos
        self.x = self.tx * TILE_SIZE + TILE_SIZE / 2
        self.y = self.ty * TILE_SIZE + TILE_SIZE / 2
        self.speed_tiles = GHOST_BASE_SPEED * speed_mult
        self.state = "chase"  # chase | scatter | fright
        self.state_time = 0.0

    def set_fright(self):
        self.state = "fright"
        self.state_time = GHOST_FRIGHT_TIME

    def update(self, dt: float, is_blocked, map_w: int, map_h: int, players: List, ghosts: List["Ghost"]):
        self.state_time = max(0.0, self.state_time - dt)
        if self.state == "fright" and self.state_time <= 0:
            self.state = "chase"

        # Chọn mục tiêu theo vai trò
        p_main = players[0]
        p_aux = players[1] if len(players) > 1 else players[0]
        px, py = p_main.pixel_center()
        ptx, pty = int(px // TILE_SIZE), int(py // TILE_SIZE)

        # Vai trò theo idx để đa dạng chiến thuật
        role = ["chase", "intercept", "herd", "ambush", "chase"][self.idx % 5]

        target = (ptx, pty)

        if role == "intercept":
            # tính ô phía trước người chơi dựa trên hướng
            dx, dy = p_main.dir
            target = (ptx + dx * 4, pty + dy * 4)
        elif role == "herd":
            # ép vào một bức tường gần: dịch mục tiêu vào trung tâm map
            cx, cy = map_w // 2, map_h // 2
            target = (int((ptx + cx) / 2), int((pty + cy) / 2))
        elif role == "ambush":
            # chặn đường giao nhau gần nhất
            dx, dy = p_main.dir
            target = (ptx + dx * 6, pty + dy * 2)

        # giới hạn biên
        tx = max(1, min(map_w - 2, target[0]))
        ty = max(1, min(map_h - 2, target[1]))
        target = (tx, ty)

        # tránh tàng hình: chuyển mục tiêu sang người chơi phụ nếu P1 tàng hình
        if p_main.is_invisible():
            ax, ay = p_aux.pixel_center()
            target = (int(ax // TILE_SIZE), int(ay // TILE_SIZE))

        # tìm đường
        cur_tile = (int(self.x // TILE_SIZE), int(self.y // TILE_SIZE))
        path = a_star(cur_tile, target, is_blocked, map_w, map_h)
        if path and len(path) >= 2:
            nxt = path[1]
        else:
            nxt = cur_tile

        # di chuyển hướng tới ô tiếp theo
        dx = (nxt[0] * TILE_SIZE + TILE_SIZE / 2) - self.x
        dy = (nxt[1] * TILE_SIZE + TILE_SIZE / 2) - self.y
        dist = max(1.0, (dx * dx + dy * dy) ** 0.5)
        speed_px = self.speed_tiles * TILE_SIZE * (0.6 if self.state == "fright" else 1.0)
        self.x += speed_px * dx / dist * dt
        self.y += speed_px * dy / dist * dt

    def hit_player(self, player) -> bool:
        # Va chạm đơn giản theo bán kính
        px, py = player.pixel_center()
        dx = self.x - px
        dy = self.y - py
        r = TILE_SIZE * 0.45
        return (dx * dx + dy * dy) <= (r * r)

    def draw(self, surf):
        col = (120, 120, 255) if self.state == "fright" else COLOR_GHOST
        pygame.draw.rect(surf, col, pygame.Rect(self.x - 10, self.y - 10, 20, 20), border_radius=6)


class Boss:
    def __init__(self, tile_pos: Tuple[int, int], speed_mult: float = 1.0):
        self.tx, self.ty = tile_pos
        self.x = self.tx * TILE_SIZE + TILE_SIZE / 2
        self.y = self.ty * TILE_SIZE + TILE_SIZE / 2
        self.speed_tiles = BOSS_SPEED * speed_mult
        self.charge_timer = 0.0
        self.health = BOSS_HEALTH

    def alive(self) -> bool:
        return self.health > 0

    def hurt(self, dmg: int):
        self.health = max(0, self.health - dmg)

    def update(self, dt: float, is_blocked, map_w: int, map_h: int, players: List[Player]):
        self.charge_timer += dt
        # Mục tiêu: điểm trung bình 2 người
        cx = sum(p.pixel_center()[0] for p in players) / max(1, len(players))
        cy = sum(p.pixel_center()[1] for p in players) / max(1, len(players))
        # lao nhanh theo chu kỳ
        mult = BOSS_CHARGE_MULT if self.charge_timer >= BOSS_CHARGE_INTERVAL else 1.0
        if self.charge_timer >= BOSS_CHARGE_INTERVAL:
            self.charge_timer = 0.0

        dx = cx - self.x
        dy = cy - self.y
        dist = max(1.0, (dx * dx + dy * dy) ** 0.5)
        speed_px = self.speed_tiles * TILE_SIZE * mult
        self.x += speed_px * dx / dist * dt
        self.y += speed_px * dy / dist * dt

    def hit_player(self, player) -> bool:
        px, py = player.pixel_center()
        dx = self.x - px
        dy = self.y - py
        r = TILE_SIZE * 0.55
        return (dx * dx + dy * dy) <= (r * r)

    def draw(self, surf):
        pygame.draw.circle(surf, COLOR_BOSS, (int(self.x), int(self.y)), TILE_SIZE // 2 + 2)
        # vẽ máu boss
        bw = 30
        br = pygame.Rect(int(self.x - bw / 2), int(self.y - TILE_SIZE), bw, 6)
        pygame.draw.rect(surf, (60, 60, 60), br, border_radius=2)
        if self.health > 0:
            frac = self.health / BOSS_HEALTH
            fg = br.copy()
            fg.width = int(br.width * frac)
            pygame.draw.rect(surf, (230, 80, 120), fg, border_radius=2)
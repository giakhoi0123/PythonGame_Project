"""
Hệ thống vật phẩm: hồi máu, bẫy, bom, khiên, tăng tốc tạm thời.
Sinh ngẫu nhiên theo thời gian, tự hủy nếu quá hạn.
"""

import random
from typing import List, Tuple, Optional
import pygame
from settings import (
    TILE_SIZE, ITEM_SPAWN_INTERVAL, ITEM_DESPAWN_TIME,
    ITEM_SCORE, SHIELD_DURATION, SPEED_BOOST_MULT, SPEED_BOOST_DURATION
)
from utils import Timer


ITEM_TYPES = ["health", "trap", "bomb", "shield", "speed"]


class Item:
    def __init__(self, item_type: str, tile_pos: Tuple[int, int]):
        self.type = item_type
        self.tx, self.ty = tile_pos
        self.timer = Timer(ITEM_DESPAWN_TIME)
        self.timer.start()

    def rect(self) -> pygame.Rect:
        x = self.tx * TILE_SIZE + TILE_SIZE // 2
        y = self.ty * TILE_SIZE + TILE_SIZE // 2
        r = TILE_SIZE // 3
        return pygame.Rect(x - r, y - r, r * 2, r * 2)

    def draw(self, surf: pygame.Surface):
        center = (self.tx * TILE_SIZE + TILE_SIZE // 2, self.ty * TILE_SIZE + TILE_SIZE // 2)
        color_map = {
            "health": (70, 220, 100),
            "trap": (230, 160, 70),
            "bomb": (230, 80, 80),
            "shield": (90, 190, 255),
            "speed": (255, 230, 120),
        }
        pygame.draw.circle(surf, color_map.get(self.type, (255, 255, 255)), center, TILE_SIZE // 3)

    def update(self, dt: float):
        self.timer.tick(dt)

    def expired(self) -> bool:
        return self.timer.ready()


class ItemsManager:
    def __init__(self, map_width: int, map_height: int, is_blocked):
        self.items: List[Item] = []
        self.spawn_timer = Timer(ITEM_SPAWN_INTERVAL)
        self.spawn_timer.start()
        self.map_w = map_width
        self.map_h = map_height
        self.is_blocked = is_blocked

    def try_spawn(self):
        for _ in range(20):
            tx = random.randint(1, self.map_w - 2)
            ty = random.randint(1, self.map_h - 2)
            if not self.is_blocked(tx, ty):
                itype = random.choice(ITEM_TYPES)
                self.items.append(Item(itype, (tx, ty)))
                break

    def update(self, dt: float):
        self.spawn_timer.tick(dt)
        if self.spawn_timer.ready():
            self.try_spawn()
            self.spawn_timer.set_and_start(ITEM_SPAWN_INTERVAL)
        for it in self.items:
            it.update(dt)
        self.items = [i for i in self.items if not i.expired()]

    def draw(self, surf: pygame.Surface):
        for it in self.items:
            it.draw(surf)

    def try_pickup(self, player, sound, particles) -> Optional[str]:
        """Kiểm tra nhặt vật phẩm; áp dụng hiệu ứng và trả về loại item (để cộng điểm)."""
        px, py = player.pixel_center()
        pr = TILE_SIZE // 2
        prect = pygame.Rect(px - pr, py - pr, pr * 2, pr * 2)
        for i, it in enumerate(self.items):
            if prect.colliderect(it.rect()):
                t = it.type
                if t == "health":
                    player.heal(1)
                elif t == "trap":
                    player.place_trap = True  # cờ để xử lý ở main (đặt bẫy gần người chơi)
                elif t == "bomb":
                    player.trigger_bomb = True  # cờ để nổ ở main
                elif t == "shield":
                    player.activate_shield(SHIELD_DURATION)
                elif t == "speed":
                    player.activate_speed(SPEED_BOOST_MULT, SPEED_BOOST_DURATION)
                sound.power()
                particles.spawn_explosion((px, py), color=(255, 240, 120), count=12)
                self.items.pop(i)
                return t
        return None
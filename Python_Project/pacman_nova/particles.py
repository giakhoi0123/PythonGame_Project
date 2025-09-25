"""
Hiệu ứng hạt: nổ, vệt tốc độ, hào quang khiên.
Giúp game sống động mà không cần asset ảnh.
"""

import random
from typing import List, Tuple
import pygame
from settings import COLOR_SPEED, COLOR_SHIELD


class Particle:
    def __init__(self, pos: Tuple[float, float], vel: Tuple[float, float], color, life: float, size: int):
        self.x, self.y = pos
        self.vx, self.vy = vel
        self.color = color
        self.life = life
        self.size = size

    def update(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surf: pygame.Surface):
        if self.life > 0:
            alpha = max(40, int(255 * min(1.0, self.life)))
            col = (*self.color, alpha)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, col, (self.size, self.size), self.size)
            surf.blit(s, (self.x - self.size, self.y - self.size))


class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []

    def spawn_explosion(self, pos: Tuple[float, float], color=(255, 160, 60), count: int = 30):
        for _ in range(count):
            ang = random.random() * 6.283
            spd = random.uniform(60, 180)
            vx = spd * float(pygame.math.Vector2(1, 0).rotate_rad(ang).x)
            vy = spd * float(pygame.math.Vector2(1, 0).rotate_rad(ang).y)
            self.particles.append(Particle(pos, (vx, vy), color, random.uniform(0.3, 0.7), random.randint(2, 4)))

    def spawn_speed_trail(self, pos: Tuple[float, float]):
        jitter = 5
        px = pos[0] + random.uniform(-jitter, jitter)
        py = pos[1] + random.uniform(-jitter, jitter)
        self.particles.append(Particle((px, py), (0, 0), COLOR_SPEED, 0.2, 2))

    def spawn_shield_glow(self, pos: Tuple[float, float]):
        self.particles.append(Particle(pos, (0, 0), COLOR_SHIELD, 0.15, 3))

    def update(self, dt: float):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surf: pygame.Surface):
        for p in self.particles:
            p.draw(surf)
"""
Giao diện: Menu, Settings, HUD (máu, điểm, kỹ năng).
"""

from typing import List
import pygame
from settings import (
    COLOR_UI_PANEL, COLOR_TEXT, COLOR_UI_ACCENT, HUD_HEIGHT,
    COLOR_HEALTH_GOOD, COLOR_HEALTH_WARN, COLOR_HEALTH_LOW, DEFAULT_VOLUME
)


class Menu:
    def __init__(self, font, sound):
        self.font = font
        self.sound = sound
        self.items = ["Start", "Settings", "Exit"]
        self.sel = 0
        self.volume = DEFAULT_VOLUME
        self.diff_idx = 1

    def handle(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(self.items)
                self.sound.menu()
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(self.items)
                self.sound.menu()

    def draw(self, surf):
        surf.fill((6, 6, 12))
        title = self.font["xl"].render("Pacman Nova", True, COLOR_UI_ACCENT)
        surf.blit(title, (surf.get_width() // 2 - title.get_width() // 2, 100))
        for i, it in enumerate(self.items):
            col = COLOR_UI_ACCENT if i == self.sel else COLOR_TEXT
            txt = self.font["lg"].render(it, True, col)
            surf.blit(txt, (surf.get_width() // 2 - txt.get_width() // 2, 220 + i * 50))

    def selected(self) -> str:
        return self.items[self.sel]


def _health_color(frac: float):
    if frac >= 0.7:
        return COLOR_HEALTH_GOOD
    if frac >= 0.35:
        return COLOR_HEALTH_WARN
    return COLOR_HEALTH_LOW


def draw_hud(surf, font, p1, p2, level_idx: int):
    w = surf.get_width()
    h = surf.get_height()
    rect = pygame.Rect(0, h - HUD_HEIGHT, w, HUD_HEIGHT)
    pygame.draw.rect(surf, COLOR_UI_PANEL, rect)

    # Điểm
    txt = font["md"].render(f"Level {level_idx + 1}  |  P1: {p1.score}  P2: {p2.score}", True, COLOR_TEXT)
    surf.blit(txt, (12, h - HUD_HEIGHT + 10))

    # Thanh máu
    def draw_hp(px, py, player, label):
        frac = player.health / max(1, player.health_max)
        bw = 200
        bh = 14
        bar = pygame.Rect(px, py, bw, bh)
        pygame.draw.rect(surf, (40, 40, 60), bar, border_radius=4)
        fg = bar.copy()
        fg.width = int(bw * frac)
        pygame.draw.rect(surf, _health_color(frac), fg, border_radius=4)
        s = font["sm"].render(label, True, COLOR_TEXT)
        surf.blit(s, (px, py - 18))

    draw_hp(12, h - 48, p1, "P1 HP")
    draw_hp(12, h - 26, p2, "P2 HP")

    # Cooldowns / trạng thái kỹ năng
    def draw_status(px, py, player, text):
        st = []
        if player.is_invisible():
            st.append("INV")
        if player.has_shield():
            st.append("SHD")
        if player.boost_timer.time_left > 0:
            st.append("SPD")
        s = font["sm"].render(text + (" [" + ", ".join(st) + "]" if st else ""), True, COLOR_TEXT)
        surf.blit(s, (px, py))

    draw_status(w - 260, h - 48, p1, "P1 Skills")
    draw_status(w - 260, h - 26, p2, "P2 Skills")
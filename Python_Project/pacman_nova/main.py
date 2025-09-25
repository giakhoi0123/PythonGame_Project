"""
Pacman Nova - bản hoàn chỉnh đơn giản, có:
- 2 người chơi, nâng cấp kỹ năng, item ngẫu nhiên
- Ghost AI phối hợp và Boss
- Âm thanh tổng hợp, hiệu ứng hạt
- Menu, HUD
Tối ưu rõ ràng để người mới đọc code vẫn hiểu.
"""

import sys
import random
import pygame

from settings import (
    TILE_SIZE, HUD_HEIGHT, COLOR_BG, COLOR_TEXT, DIFFICULTIES, UPGRADES,
    PELLET_SCORE, ITEM_SCORE, GHOST_SCORE, BOSS_SCORE, POWER_FRIGHT_BONUS,
    DEFAULT_VOLUME, COLOR_P1, COLOR_P2
)
from utils import Timer
from map import GameMap
from player import Player
from src.enemy import Ghost, Boss
from items import ItemsManager
from particles import ParticleSystem
from src.audio import SoundManager
from src.ui import Menu, draw_hud


def grid_surface(gmap: GameMap):
    w = gmap.w * TILE_SIZE
    h = gmap.h * TILE_SIZE
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    gmap.draw(surf)
    return surf


def main():
    pygame.init()
    pygame.display.set_caption("Pacman Nova")
    screen = pygame.display.set_mode((24 * 24, 17 * 24 + HUD_HEIGHT))  # phù hợp map
    clock = pygame.time.Clock()

    # Font
    font = {
        "sm": pygame.font.SysFont("arial", 14),
        "md": pygame.font.SysFont("arial", 18, bold=True),
        "lg": pygame.font.SysFont("arial", 24, bold=True),
        "xl": pygame.font.SysFont("arial", 36, bold=True),
    }

    sound = SoundManager(DEFAULT_VOLUME)

    # State
    STATE_MENU = "menu"
    STATE_SETTINGS = "settings"
    STATE_PLAY = "play"
    STATE_UPGRADE = "upgrade"
    STATE_GAMEOVER = "gameover"
    state = STATE_MENU

    menu = Menu(font, sound)
    diff_idx = 1

    level_idx = 0
    gmap = GameMap(level_idx)
    map_surf = grid_surface(gmap)

    # Entities
    p1 = Player(1, gmap.p1_spawn, COLOR_P1)
    p2 = Player(2, gmap.p2_spawn, COLOR_P2)
    players = [p1, p2]

    ghosts = []
    boss = None

    items = ItemsManager(gmap.w, gmap.h, gmap.is_blocked)
    particles = ParticleSystem()

    fright_timer = Timer(0.0)

    def start_level(idx: int):
        nonlocal gmap, map_surf, ghosts, boss, level_idx, items
        level_idx = idx
        gmap = GameMap(level_idx)
        map_surf = grid_surface(gmap)
        items = ItemsManager(gmap.w, gmap.h, gmap.is_blocked)

        # đặt người chơi về spawn
        for i, pl in enumerate(players):
            spawn = gmap.p1_spawn if i == 0 else gmap.p2_spawn
            pl.tx, pl.ty = spawn
            pl.x = spawn[0] * TILE_SIZE + TILE_SIZE / 2
            pl.y = spawn[1] * TILE_SIZE + TILE_SIZE / 2
            pl.dir = (0, 0)

        # sinh ghost và boss theo độ khó
        d = DIFFICULTIES[diff_idx]
        ghosts = []
        for i in range(d.ghost_count):
            # spawn quanh trung tâm
            gx = gmap.w // 2 + random.randint(-3, 3)
            gy = gmap.h // 2 + random.randint(-2, 2)
            gx = max(1, min(gmap.w - 2, gx))
            gy = max(1, min(gmap.h - 2, gy))
            if not gmap.is_blocked(gx, gy):
                ghosts.append(Ghost(i, (gx, gy), speed_mult=d.ghost_speed_mult))
        if d.boss_present and level_idx % 2 == 1:
            boss = Boss(gmap.boss_spawn, speed_mult=d.ghost_speed_mult)
        else:
            boss = None
        return ghosts, boss

    ghosts, boss = start_level(level_idx)

    # UI phụ
    def draw_world():
        screen.fill(COLOR_BG)
        screen.blit(map_surf, (0, 0))
        items.draw(screen)
        for g in ghosts:
            g.draw(screen)
        if boss and boss.alive():
            boss.draw(screen)
        for pl in players:
            pl.draw(screen)
        particles.draw(screen)
        draw_hud(screen, font, p1, p2, level_idx)

    # Vòng game
    running = True
    while running:
        dt = min(0.033, clock.tick(60) / 1000.0)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if state == STATE_MENU:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    sel = menu.selected()
                    if sel == "Start":
                        sound.menu()
                        state = STATE_PLAY
                        p1.score = 0
                        p2.score = 0
                        p1.health = p1.health_max
                        p2.health = p2.health_max
                        level_idx = 0
                        ghosts, boss = start_level(level_idx)
                    elif sel == "Settings":
                        state = STATE_SETTINGS
                        sound.menu()
                    elif sel == "Exit":
                        running = False
                else:
                    menu.handle(ev)
            elif state == STATE_SETTINGS:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        state = STATE_MENU
                        sound.menu()
                    elif ev.key in (pygame.K_LEFT, pygame.K_a):
                        diff_idx = (diff_idx - 1) % len(DIFFICULTIES)
                        sound.menu()
                    elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                        diff_idx = (diff_idx + 1) % len(DIFFICULTIES)
                        sound.menu()
            elif state == STATE_UPGRADE:
                if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    idx = {pygame.K_1:0, pygame.K_2:1, pygame.K_3:2, pygame.K_4:3}[ev.key]
                    # Mỗi người chọn một upgrade giống nhau cho đơn giản
                    p1.upgrade(UPGRADES[idx])
                    p2.upgrade(UPGRADES[idx])
                    state = STATE_PLAY
                    ghosts, boss = start_level(level_idx)

            elif state == STATE_GAMEOVER:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN:
                        state = STATE_MENU
                        sound.menu()

        keys = pygame.key.get_pressed()

        if state == STATE_MENU:
            menu.draw(screen)
            # settings hint
            s = font["sm"].render("Use Up/Down + Enter. Settings: change difficulty with Left/Right. Esc to back.", True, COLOR_TEXT)
            screen.blit(s, (screen.get_width()//2 - s.get_width()//2, screen.get_height()-60))

        elif state == STATE_SETTINGS:
            screen.fill((8, 8, 16))
            t = font["xl"].render("Settings", True, COLOR_TEXT)
            screen.blit(t, (screen.get_width()//2 - t.get_width()//2, 80))
            d = DIFFICULTIES[diff_idx]
            dtxt = font["lg"].render(f"Difficulty: {d.name} (ghosts={d.ghost_count}, boss={'Yes' if d.boss_present else 'No'})", True, COLOR_TEXT)
            screen.blit(dtxt, (screen.get_width()//2 - dtxt.get_width()//2, 180))
            hint = font["sm"].render("Left/Right to change. Esc to return.", True, COLOR_TEXT)
            screen.blit(hint, (screen.get_width()//2 - hint.get_width()//2, 230))

        elif state == STATE_PLAY:
            # Input & kỹ năng
            p1.handle_input(keys, True)
            p1.handle_skills(keys, True)
            p2.handle_input(keys, False)
            p2.handle_skills(keys, False)

            # Hút pellet nếu nam châm (đơn giản: ăn pellet trong bán kính)
            for pl in (p1, p2):
                rad = pl.magnet_pulse_radius()
                cx, cy = pl.pixel_center()
                # quét một vùng nhỏ lân cận
                min_tx = int(max(0, (cx - rad) // TILE_SIZE))
                max_tx = int(min(gmap.w - 1, (cx + rad) // TILE_SIZE))
                min_ty = int(max(0, (cy - rad) // TILE_SIZE))
                max_ty = int(min(gmap.h - 1, (cy + rad) // TILE_SIZE))
                eaten = 0
                for ty in range(min_ty, max_ty + 1):
                    for tx in range(min_tx, max_tx + 1):
                        if (tx, ty) in gmap.pellets:
                            px = tx * TILE_SIZE + TILE_SIZE // 2
                            py = ty * TILE_SIZE + TILE_SIZE // 2
                            dx = px - cx
                            dy = py - cy
                            if dx * dx + dy * dy <= rad * rad:
                                eaten += gmap.eat_pellet(tx, ty)
                if eaten:
                    sc = eaten * PELLET_SCORE
                    pl.score += sc
                    sound.eat()

            # Ăn power pellet
            for pl in (p1, p2):
                tx = int(pl.x // TILE_SIZE)
                ty = int(pl.y // TILE_SIZE)
                if gmap.eat_power(tx, ty):
                    for g in ghosts:
                        g.set_fright()
                    pl.score += POWER_FRIGHT_BONUS
                    sound.power()

            # Ăn pellet khi đi qua tâm ô
            for pl in (p1, p2):
                tx = int(pl.x // TILE_SIZE)
                ty = int(pl.y // TILE_SIZE)
                if gmap.eat_pellet(tx, ty):
                    pl.score += PELLET_SCORE
                    sound.eat()

            # Nhặt item
            for pl in (p1, p2):
                got = items.try_pickup(pl, sound, particles)
                if got:
                    pl.score += ITEM_SCORE

            # Cập nhật logic
            p1.update(dt, gmap.is_blocked)
            p2.update(dt, gmap.is_blocked)
            items.update(dt)
            particles.update(dt)

            # Ghost cập nhật
            for g in ghosts:
                g.update(dt, gmap.is_blocked, gmap.w, gmap.h, players, ghosts)

            # Boss cập nhật
            if boss and boss.alive():
                boss.update(dt, gmap.is_blocked, gmap.w, gmap.h, players)

            # Xử lý bomb / trap từ item
            for pl in (p1, p2):
                if pl.trigger_bomb:
                    sound.explosion()
                    particles.spawn_explosion(pl.pixel_center(), count=40)
                    # dọa ma: nếu ma trong bán kính thì fright
                    bx, by = pl.pixel_center()
                    r2 = (TILE_SIZE * 5) ** 2
                    for g in ghosts:
                        dx = g.x - bx
                        dy = g.y - by
                        if dx * dx + dy * dy <= r2:
                            g.set_fright()
                    # gây sát thương lên boss
                    if boss and boss.alive():
                        dx = boss.x - bx
                        dy = boss.y - by
                        if dx * dx + dy * dy <= r2:
                            boss.hurt(2)
                            pl.score += 100
                    pl.trigger_bomb = False
                if pl.place_trap:
                    # đơn giản: đặt bẫy làm chậm ma (biến fright ngắn)
                    bx, by = pl.pixel_center()
                    for g in ghosts:
                        dx = g.x - bx
                        dy = g.y - by
                        if dx * dx + dy * dy <= (TILE_SIZE * 2) ** 2:
                            g.set_fright()
                    pl.place_trap = False

            # Va chạm ma -> gây sát thương
            for g in ghosts[:]:
                for pl in (p1, p2):
                    if g.hit_player(pl) and not pl.is_invisible():
                        pl.hurt(1)
                        sound.hit()
                        # thưởng khi ma đang fright (coi như hạ ma)
                        if g.state == "fright":
                            pl.score += GHOST_SCORE
                            ghosts.remove(g)
                            break

            # Va chạm boss
            if boss and boss.alive():
                for pl in (p1, p2):
                    if boss.hit_player(pl) and not pl.is_invisible():
                        pl.hurt(2)
                        sound.hit()

            # Thua
            if p1.health <= 0 and p2.health <= 0:
                state = STATE_GAMEOVER
                sound.hit()

            # Thắng level khi hết pellet
            if gmap.pellets_remaining() == 0 and (not boss or not boss.alive()):
                # thưởng
                p1.score += 200
                p2.score += 200
                sound.power()
                # chọn nâng cấp
                level_idx += 1
                if level_idx >= len(GameMap.__dict__.get("LEVELS", [0, 1, 2])):  # không dùng; chỉ để linter yên
                    pass
                state = STATE_UPGRADE

            # Vẽ
            draw_world()

        elif state == STATE_UPGRADE:
            screen.fill((10, 10, 18))
            t = font["xl"].render("Chọn nâng cấp (1-4)", True, COLOR_TEXT)
            screen.blit(t, (screen.get_width()//2 - t.get_width()//2, 80))
            for i, up in enumerate(UPGRADES):
                line = font["lg"].render(f"{i+1}. {up}", True, COLOR_TEXT)
                screen.blit(line, (screen.get_width()//2 - line.get_width()//2, 160 + i * 40))
            s = font["sm"].render("Sau khi chọn, level tiếp theo sẽ bắt đầu.", True, COLOR_TEXT)
            screen.blit(s, (screen.get_width()//2 - s.get_width()//2, 340))

        elif state == STATE_GAMEOVER:
            screen.fill((8, 8, 16))
            t = font["xl"].render("Game Over", True, COLOR_TEXT)
            screen.blit(t, (screen.get_width()//2 - t.get_width()//2, 120))
            sc = font["lg"].render(f"Score P1: {p1.score}  |  Score P2: {p2.score}", True, COLOR_TEXT)
            screen.blit(sc, (screen.get_width()//2 - sc.get_width()//2, 200))
            h = font["md"].render("Press Enter to return to Menu", True, COLOR_TEXT)
            screen.blit(h, (screen.get_width()//2 - h.get_width()//2, 260))

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
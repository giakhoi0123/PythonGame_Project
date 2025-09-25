"""
Quản lý bản đồ, pellet, power pellet, và va chạm tường.
Bao gồm nhiều màn chơi với độ khó tăng dần.
"""

from typing import List, Set, Tuple
import pygame
from settings import TILE_SIZE, GRID_OUTLINE, COLOR_WALL, COLOR_PELLET, COLOR_POWER

LevelStr = List[str]


LEVELS: List[LevelStr] = [
    # Level 1
    [
        "XXXXXXXXXXXXXXXXXXXXXXXXX",
        "X.........X.....X......X",
        "X.XXX.XXX.X.XXX.X.XXXX.X",
        "X.X.....X...X.....X....X",
        "X.X.XXX.XXXXX.XXX.X.XX.X",
        "X...X.............X....X",
        "XXX.X.XXX.XXX.XXX.X.XXXX",
        "X...X.X...X...X...X....X",
        "X.XXX.X.XXX.B.XXX.X.XX.X",
        "X.....X...P.....Q.X....X",
        "X.XXX.XXX.XXX.XXX.XXX..X",
        "X.X........O........X..X",
        "X.X.XXX.XXXXX.XXX.X.XX.X",
        "X.X.....X...X.....X....X",
        "X.XXX.XXX.X.XXX.X.XX.X.X",
        "X.........X.....X......X",
        "XXXXXXXXXXXXXXXXXXXXXXXXX",
    ],
    # Level 2
    [
        "XXXXXXXXXXXXXXXXXXXXXXXXX",
        "X.....X....X....X......X",
        "X.XXX.X.XX.X.XX.X.XXXX.X",
        "X.X...X..X...X..X...X..X",
        "X.X.XXXXX.XXX.XXXXX.X..X",
        "X...X.............X....X",
        "XXX.X.XXX.XXX.XXX.X.XXXX",
        "X...X.X...X...X...X....X",
        "X.XXX.X.XXX.B.XXX.X.XX.X",
        "X..O..X...P.....Q.X..O.X",
        "X.XXX.XXX.XXX.XXX.XXX..X",
        "X.X........O........X..X",
        "X.X.XXX.XXXXX.XXX.XXX..X",
        "X.X.....X...X.....X....X",
        "X.XXX.XXX.X.XXX.X.XX.X.X",
        "X.....X....X....X......X",
        "XXXXXXXXXXXXXXXXXXXXXXXXX",
    ],
    # Level 3 (hẹp hơn, boss khó hơn)
    [
        "XXXXXXXXXXXXXXXXXXXXXXXXX",
        "X...X...X...X...X......X",
        "X.X.X.X.X.X.X.X.X.XXXX.X",
        "X.X.X.X.X.X.X.X.X.X..X.X",
        "X.X.X.XXX.B.XXX.X.X..X.X",
        "X......................X",
        "XXX.XXX.XXX.XXX.XXX.XXXX",
        "X...X...X...X...X....O.X",
        "X.XXX.XXX.XXX.XXX.XX.X.X",
        "X.....X...P.....Q.X....X",
        "X.XXX.XXX.XXX.XXX.XXX..X",
        "X.O..................O.X",
        "X.XXX.XXX.XXX.XXX.XXX..X",
        "X...X...X...X...X......X",
        "X.X.X.X.X.X.X.X.X.XX.X.X",
        "X...X...X...X...X......X",
        "XXXXXXXXXXXXXXXXXXXXXXXXX",
    ],
]


class GameMap:
    def __init__(self, level_index: int):
        self.level = LEVELS[level_index % len(LEVELS)]
        self.h = len(self.level)
        self.w = len(self.level[0])
        self.walls: Set[Tuple[int, int]] = set()
        self.pellets: Set[Tuple[int, int]] = set()
        self.powers: Set[Tuple[int, int]] = set()
        self.boss_spawn: Tuple[int, int] = (self.w // 2, self.h // 2)
        self.p1_spawn: Tuple[int, int] = (1, 1)
        self.p2_spawn: Tuple[int, int] = (self.w - 2, self.h - 2)
        self._parse()

    def _parse(self):
        for y, row in enumerate(self.level):
            for x, ch in enumerate(row):
                if ch == "X":
                    self.walls.add((x, y))
                elif ch == ".":
                    self.pellets.add((x, y))
                elif ch == "O":
                    self.powers.add((x, y))
                elif ch == "P":
                    self.p1_spawn = (x, y)
                    self.pellets.add((x, y))
                elif ch == "Q":
                    self.p2_spawn = (x, y)
                    self.pellets.add((x, y))
                elif ch == "B":
                    self.boss_spawn = (x, y)
                    self.pellets.add((x, y))
                else:
                    self.pellets.add((x, y)) if ch != "X" else None

    def is_blocked(self, x: int, y: int) -> bool:
        return (x, y) in self.walls

    def pellet_at(self, x: int, y: int) -> bool:
        return (x, y) in self.pellets

    def power_at(self, x: int, y: int) -> bool:
        return (x, y) in self.powers

    def eat_pellet(self, x: int, y: int) -> int:
        if (x, y) in self.pellets:
            self.pellets.remove((x, y))
            return 1
        return 0

    def eat_power(self, x: int, y: int) -> int:
        if (x, y) in self.powers:
            self.powers.remove((x, y))
            return 1
        return 0

    def pellets_remaining(self) -> int:
        return len(self.pellets) + len(self.powers)

    def draw(self, surf: pygame.Surface):
        # Vẽ tường
        for (x, y) in self.walls:
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surf, COLOR_WALL, rect)
            pygame.draw.rect(surf, (0, 0, 0), rect, GRID_OUTLINE)

        # Vẽ pellet
        for (x, y) in self.pellets:
            cx = x * TILE_SIZE + TILE_SIZE // 2
            cy = y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(surf, COLOR_PELLET, (cx, cy), 3)

        # Vẽ power pellet
        for (x, y) in self.powers:
            cx = x * TILE_SIZE + TILE_SIZE // 2
            cy = y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(surf, COLOR_POWER, (cx, cy), 6)
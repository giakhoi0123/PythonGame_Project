"""
Tiện ích: toán học lưới, tìm đường A*, bộ đếm thời gian, easing đơn giản.
"""

from __future__ import annotations

from dataclasses import dataclass
import heapq
from typing import Dict, Iterable, List, Optional, Set, Tuple, Callable

GridPos = Tuple[int, int]


def manhattan(a: GridPos, b: GridPos) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbors_4(grid_width: int, grid_height: int, cell: GridPos) -> Iterable[GridPos]:
    x, y = cell
    if x > 0:
        yield (x - 1, y)
    if x < grid_width - 1:
        yield (x + 1, y)
    if y > 0:
        yield (x, y - 1)
    if y < grid_height - 1:
        yield (x, y + 1)


def reconstruct_path(came_from: Dict[GridPos, GridPos], current: GridPos) -> List[GridPos]:
    path: List[GridPos] = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def a_star(
    start: GridPos,
    goal: GridPos,
    is_blocked: Callable[[int, int], bool],
    grid_width: int,
    grid_height: int,
    max_expansions: int = 3000,
) -> Optional[List[GridPos]]:
    """
    A* cơ bản trên lưới 4 hướng. is_blocked trả True nếu là tường.
    Trả về danh sách các ô từ start đến goal (bao gồm), hoặc None nếu không có đường.
    """
    if start == goal:
        return [start]

    open_heap: List[Tuple[int, GridPos]] = []
    heapq.heappush(open_heap, (0, start))
    came_from: Dict[GridPos, GridPos] = {}
    g_score: Dict[GridPos, int] = {start: 0}
    f_score: Dict[GridPos, int] = {start: manhattan(start, goal)}
    seen: Set[GridPos] = {start}

    expansions = 0
    while open_heap and expansions < max_expansions:
        _, current = heapq.heappop(open_heap)
        if current == goal:
            return reconstruct_path(came_from, current)
        for nxt in neighbors_4(grid_width, grid_height, current):
            if is_blocked(nxt[0], nxt[1]):
                continue
            tentative_g = g_score[current] + 1
            if nxt not in g_score or tentative_g < g_score[nxt]:
                came_from[nxt] = current
                g_score[nxt] = tentative_g
                f = tentative_g + manhattan(nxt, goal)
                f_score[nxt] = f
                if nxt not in seen:
                    heapq.heappush(open_heap, (f, nxt))
                    seen.add(nxt)
        expansions += 1
    return None


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def approach(current: float, target: float, delta: float) -> float:
    """Di chuyển current tới target tối đa delta."""
    if current < target:
        return min(target, current + delta)
    else:
        return max(target, current - delta)


@dataclass
class Timer:
    duration: float
    time_left: float = 0.0

    def start(self):
        self.time_left = self.duration

    def set_and_start(self, duration: float):
        self.duration = duration
        self.time_left = duration

    def tick(self, dt: float):
        if self.time_left > 0.0:
            self.time_left = max(0.0, self.time_left - dt)

    def ready(self) -> bool:
        return self.time_left <= 0.0
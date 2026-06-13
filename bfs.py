#!/usr/bin/env python3

from collections import deque
from typing import Optional, List, Tuple, Deque
from constants import NORTH, EAST, SOUTH, WEST


def reconstruct_path(
    parent: dict[tuple[int, int], tuple[tuple[int, int], str]],
    entry: tuple[int, int],
    exit: tuple[int, int]
) -> Optional[str]:
    """Reconstructs the shortest path from entry to exit."""
    path = []
    current = exit
    while current != entry:
        current, direction = parent[current]
        path.append(direction)
    path.reverse()
    return ''.join(path)


def bfs(maze: List[List[int]],
        entry: tuple[int, int],
        exit: tuple[int, int]) -> Optional[str]:
    """Finds shortest path from entry to exit using the BFS algorithm."""
    queue: Deque[Tuple[int, int]] = deque()
    visited: set[Tuple[int, int]] = set()
    parent: dict[Tuple[int, int], Tuple[Tuple[int, int], str]] = {}

    queue.append(entry)
    visited.add(entry)

    while queue:
        current = queue.popleft()
        if current == exit:
            return reconstruct_path(parent, entry, exit)
        x, y = current
        # if is part of the gallery == 0
        if maze[y][x] & SOUTH == 0 and y + 1 < len(maze):
            neighbor = (x, y + 1)
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = (current, 'S')
                queue.append(neighbor)
        if maze[y][x] & NORTH == 0 and y - 1 >= 0:
            neighbor = (x, y - 1)
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = (current, 'N')
                queue.append(neighbor)
        if maze[y][x] & EAST == 0 and x + 1 < len(maze[0]):
            neighbor = (x + 1, y)
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = (current, 'E')
                queue.append(neighbor)
        if maze[y][x] & WEST == 0 and x - 1 >= 0:
            neighbor = (x - 1, y)
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = (current, 'W')
                queue.append(neighbor)

    return None

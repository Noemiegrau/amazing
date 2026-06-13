import random
from collections import deque
from typing import Optional

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


class Maze():

    DIRECTIONS: list[tuple[int, tuple[int, int], int]] = [
        (1, (0, -1), 4),
        (2, (1, 0), 8),
        (4, (0, 1), 1),
        (8, (-1, 0), 2),
    ]

    PATTERN_4: list[tuple[int, int]] = [
        (0, 0), (0, 1),                          # colonne gauche haut
        (0, 2), (1, 2), (2, 2), (3, 2),          # barre horizontale
        (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),  # colonne droite
    ]

    PATTERN_2: list[tuple[int, int]] = [
        (0, 0), (1, 0), (2, 0), (3, 0),  # barre haute
        (3, 1),                            # droite
        (0, 2), (1, 2), (2, 2), (3, 2),  # barre milieu
        (0, 3),                            # gauche
        (0, 4), (1, 4), (2, 4), (3, 4),  # barre basse
    ]

    PATTERN_42_WIDTH: int = 9
    PATTERN_42_HEIGHT: int = 5

    def __init__(self, width: int,
                 height: int,
                 entry: tuple[int, int],
                 exit: tuple[int, int]) -> None:
        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = exit

        self.grid: list[list[int]] = []
        row: list[int] = []
        x: int = 0
        y: int = 0
        while y < self.height:
            while x < self.width:
                row.append(0xF)
                x += 1
            self.grid.append(row)
            row = []
            x = 0
            y += 1

    def open_wall(self, x: int, y: int, direction: int) -> None:
        for dir_bit, offset, opposite in self.DIRECTIONS:
            if dir_bit == direction:
                break

        neighbor_x = x + offset[0]
        neighbor_y = y + offset[1]

        self.grid[y][x] = self.grid[y][x] & ~direction
        self.grid[neighbor_y][neighbor_x] = (self.grid[neighbor_y][neighbor_x]
                                             & ~opposite)

    def close_wall(self, x: int, y: int, direction: int) -> None:
        for dir_bit, offset, opposite in self.DIRECTIONS:
            if dir_bit == direction:
                break

        neighbor_x = x + offset[0]
        neighbor_y = y + offset[1]

        self.grid[y][x] = self.grid[y][x] | direction
        self.grid[neighbor_y][neighbor_x] = (self.grid[neighbor_y][neighbor_x]
                                             | opposite)

    def is_valid(self, x: int, y: int) -> bool:
        return (0 <= x < self.width and 0 <= y < self.height)

    def has_wall(self, x: int, y: int, direction: int) -> bool:
        return bool(self.grid[y][x] & direction)

    def get_cell(self, x: int, y: int) -> str:
        return f'{self.grid[y][x]:X}'

    def can_move(self, x: int, y: int, direction: int) -> bool:
        return not self.has_wall(x, y, direction)

    def get_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        res: list[tuple[int, int]] = []
        for dir_bit, offset, opposite in self.DIRECTIONS:
            nx, ny = x + offset[0], y + offset[1]
            if self.is_valid(nx, ny):
                res.append((nx, ny))
        return res

    def to_hex(self) -> str:
        res: str = ''
        for row in self.grid:
            for cell in row:
                res += f'{cell:X}'
            res += '\n'
        return res

    def get_pattern_42(self) -> list[tuple[int, int]]:

        offset_x = (self.width - self.PATTERN_42_WIDTH) // 2
        offset_y = (self.height - self.PATTERN_42_HEIGHT) // 2

        cells: list[tuple[int, int]] = []

        # le 4 (décalé à sa position)
        for px, py in self.PATTERN_4:
            cells.append((offset_x + px, offset_y + py))

        # le 2 (décalé de 5 colonnes après le 4 : 4 de largeur + 1 espace)
        for px, py in self.PATTERN_2:
            cells.append((offset_x + 5 + px, offset_y + py))

        return cells

    def generate(self, seed: int) -> None:

        random.seed(seed)

        visite: set[tuple[int, int]] = set()

        if (self.width > self.PATTERN_42_WIDTH + 1
                and self.height > self.PATTERN_42_HEIGHT + 1):
            for cell in self.get_pattern_42():
                visite.add(cell)
        else:
            print('Warning: maze too small for 42 pattern')

        start: tuple[int, int] = (0, 0)
        for sy in range(self.height):
            for sx in range(self.width):
                if (sx, sy) not in visite:
                    start = (sx, sy)
                    break
            if start not in visite:
                break

        pile: list[tuple[int, int]] = [start]
        visite.add(start)

        while pile:
            position = pile[-1]
            x, y = position

            voisins: list[tuple[int, int]] = []
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height
                        and (nx, ny) not in visite):
                    voisins.append((nx, ny))

            if voisins:
                choice = random.choice(voisins)
                dx = choice[0] - x
                dy = choice[1] - y
                for dir_bit, offset, opposite in self.DIRECTIONS:
                    if offset == (dx, dy):
                        self.open_wall(x, y, dir_bit)
                        break
                visite.add(choice)
                pile.append(choice)
            else:
                pile.pop()

    def has_3x3_open(self, x: int, y: int) -> bool:
        """Vérifie si un bloc 3x3 commençant à (x,y) est totalement ouvert."""
        for dy in range(3):
            for dx in range(2):
                if self.has_wall(x + dx, y + dy, EAST):
                    return False
        for dy in range(2):
            for dx in range(3):
                if self.has_wall(x + dx, y + dy, SOUTH):
                    return False
        return True

    def make_imperfect(self, nb_walls_to_open: int) -> None:
        compteur: int = 0
        tentatives: int = 0
        max_tentatives = nb_walls_to_open * 10

        while compteur < nb_walls_to_open and tentatives < max_tentatives:
            tentatives += 1
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            dir_bit, offset, opposite = random.choice(self.DIRECTIONS)
            neighbor_x = x + offset[0]
            neighbor_y = y + offset[1]

            if not self.is_valid(neighbor_x, neighbor_y):
                continue

            if not self.has_wall(x, y, dir_bit):
                continue

            if (self.grid[y][x] == 0xF or
                    self.grid[neighbor_y][neighbor_x] == 0xF):
                continue

            self.open_wall(x, y, dir_bit)

            violation: bool = False
            for by in range(max(0, y - 2), min(self.height - 2, y + 1)):
                for bx in range(max(0, x - 2), min(self.width - 2, x + 1)):
                    if self.has_3x3_open(bx, by):
                        violation = True
                        break
                if violation:
                    break

            if violation:
                self.close_wall(x, y, dir_bit)
                continue

            compteur += 1

    def solve(self) -> Optional[str]:
        """Find shortest path from entry to exit using BFS.

        Returns:
            A string of N/E/S/W directions, or None if no
            path exists.
        """
        direction_map: list[tuple[int, int, int, str]] = [
            (NORTH, 0, -1, 'N'),
            (EAST, 1, 0, 'E'),
            (SOUTH, 0, 1, 'S'),
            (WEST, -1, 0, 'W'),
        ]
        queue: deque[tuple[int, int]] = deque([self.entry])
        visited: set[tuple[int, int]] = {self.entry}
        parent: dict[
            tuple[int, int],
            tuple[tuple[int, int], str]
        ] = {}

        while queue:
            x, y = queue.popleft()
            if (x, y) == self.exit:
                path: list[str] = []
                current = self.exit
                while current != self.entry:
                    current, d = parent[current]
                    path.append(d)
                path.reverse()
                return ''.join(path)
            for wall, dx, dy, letter in direction_map:
                if self.grid[y][x] & wall == 0:
                    nx, ny = x + dx, y + dy
                    if (self.is_valid(nx, ny)
                            and (nx, ny) not in visited):
                        visited.add((nx, ny))
                        parent[(nx, ny)] = ((x, y), letter)
                        queue.append((nx, ny))
        return None

#!/usr/bin/env python3

from constants import NORTH, EAST, SOUTH, WEST
from typing import Any, List
from maze import Maze
from bfs import bfs
import random
import curses


def create_grid(maze: List[List[int]]) -> List[List[int]]:
    """Build the display grid x2 bigger, to add walls."""
    height = len(maze)
    width = len(maze[0])
    grid = []
    for y in range(2 * height + 1):
        row = []
        for x in range(2 * width + 1):
            row.append(1)
        grid.append(row)
    return grid


def create_gallery(maze: List[List[int]],
                   grid: List[List[int]],
                   show_42: bool = True) -> List[List[int]]:
    """Open walls to create a path in the maze thats full with 1s."""
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            cell = maze[y][x]
            pos_x = 2 * x + 1
            pos_y = 2 * y + 1

            if cell == 0xF and show_42:
                grid[pos_y][pos_x] = 2
            else:
                grid[pos_y][pos_x] = 0

            if cell & NORTH == 0:
                grid[pos_y - 1][pos_x] = 0

            if cell & EAST == 0:
                grid[pos_y][pos_x + 1] = 0

            if cell & SOUTH == 0:
                grid[pos_y + 1][pos_x] = 0

            if cell & WEST == 0:
                grid[pos_y][pos_x - 1] = 0

    return grid


def display_path(grid: List[List[int]], path: str,
                 entry: tuple[int, int]) -> None:
    """Display the path from entry to exit."""
    current_x = 2 * entry[0] + 1
    current_y = 2 * entry[1] + 1
    step = 0
    grid[current_y][current_x] = 100 + step
    for letter in path:
        step += 1
        if letter == 'N':
            grid[current_y - 1][current_x] = 100 + step
            step += 1
            grid[current_y - 2][current_x] = 100 + step
            current_y -= 2
        elif letter == 'S':
            grid[current_y + 1][current_x] = 100 + step
            step += 1
            grid[current_y + 2][current_x] = 100 + step
            current_y += 2
        elif letter == 'E':
            grid[current_y][current_x + 1] = 100 + step
            step += 1
            grid[current_y][current_x + 2] = 100 + step
            current_x += 2
        elif letter == 'W':
            grid[current_y][current_x - 1] = 100 + step
            step += 1
            grid[current_y][current_x - 2] = 100 + step
            current_x -= 2


def animate_generation(stdscr: curses.window,
                       maze: Maze,
                       seed: int,
                       config: dict[str, Any]) -> None:
    """Animate maze generation step by step."""
    random.seed(seed)

    # Reset grid to all walls
    for y in range(maze.height):
        for x in range(maze.width):
            maze.grid[y][x] = 0xF

    visite: set[tuple[int, int]] = set()

    pattern_cells: set[tuple[int, int]] = set()
    if (maze.width > Maze.PATTERN_42_WIDTH + 1
            and maze.height > Maze.PATTERN_42_HEIGHT + 1):
        for cell in maze.get_pattern_42():
            visite.add(cell)
            pattern_cells.add(cell)

    start: tuple[int, int] = (0, 0)
    for sy in range(maze.height):
        for sx in range(maze.width):
            if (sx, sy) not in visite:
                start = (sx, sy)
                break
        if start not in visite:
            break

    pile: list[tuple[int, int]] = [start]
    visite.add(start)

    curses.init_color(41, 0, 800, 0)
    curses.init_pair(20, curses.COLOR_BLACK, 41)
    curses.init_color(42, 400, 400, 400)
    curses.init_pair(21, curses.COLOR_BLACK, 42)

    stdscr.timeout(5)

    while pile:
        position = pile[-1]
        x, y = position

        voisins: list[tuple[int, int]] = []
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < maze.width
                    and 0 <= ny < maze.height
                    and (nx, ny) not in visite):
                voisins.append((nx, ny))

        if voisins:
            choice = random.choice(voisins)
            dx = choice[0] - x
            dy = choice[1] - y
            for dir_bit, offset, opposite in Maze.DIRECTIONS:
                if offset == (dx, dy):
                    maze.open_wall(x, y, dir_bit)
                    break
            visite.add(choice)
            pile.append(choice)
        else:
            pile.pop()

        # Render
        grid = create_grid(maze.grid)
        create_gallery(maze.grid, grid, True)
        stdscr.clear()
        for gy in range(len(grid)):
            for gx in range(len(grid[0])):
                cx = min(gx // 2, maze.width - 1)
                cy = min(gy // 2, maze.height - 1)
                if (cx, cy) in pattern_cells and grid[gy][gx] == 2:
                    stdscr.addstr(gy, gx * 2, '  ',
                                  curses.color_pair(1))
                elif (cx, cy) == position and grid[gy][gx] == 0:
                    stdscr.addstr(gy, gx * 2, '  ',
                                  curses.color_pair(20))
                elif grid[gy][gx] == 0:
                    stdscr.addstr(gy, gx * 2, '  ')
                else:
                    stdscr.addstr(gy, gx * 2, '  ',
                                  curses.color_pair(5))

        info_y: int = 2 * config['HEIGHT'] + 2
        stdscr.addstr(
            info_y, 0, "Generating maze... (ESC to skip)"
        )
        stdscr.refresh()

        key = stdscr.getch()
        if key == 27:
            # Finish generation instantly
            while pile:
                pos = pile[-1]
                px, py = pos
                vs: list[tuple[int, int]] = []
                for ddx, ddy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                    nnx, nny = px + ddx, py + ddy
                    if (0 <= nnx < maze.width
                            and 0 <= nny < maze.height
                            and (nnx, nny) not in visite):
                        vs.append((nnx, nny))
                if vs:
                    ch = random.choice(vs)
                    ddx = ch[0] - px
                    ddy = ch[1] - py
                    for db, off, opp in Maze.DIRECTIONS:
                        if off == (ddx, ddy):
                            maze.open_wall(px, py, db)
                            break
                    visite.add(ch)
                    pile.append(ch)
                else:
                    pile.pop()
            break

    stdscr.timeout(150)


def display_grid(stdscr: curses.window,
                 grid: List[List[int]],
                 entry: tuple[int, int],
                 exit: tuple[int, int],
                 show_42: bool,
                 rainbow_offset: int = 0) -> None:
    """Display the final big maze, with entry and exit in color."""
    entry_x = 2 * entry[0] + 1
    entry_y = 2 * entry[1] + 1
    exit_x = 2 * exit[0] + 1
    exit_y = 2 * exit[1] + 1
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x] == 2:
                if show_42:
                    stdscr.addstr(y, x * 2, '  ',
                                  curses.color_pair(1))
                else:
                    stdscr.addstr(y, x * 2, '  ',
                                  curses.color_pair(5))
            elif x == entry_x and y == entry_y:
                stdscr.addstr(y, x * 2, '  ',
                              curses.color_pair(2))
            elif x == exit_x and y == exit_y:
                stdscr.addstr(y, x * 2, '  ',
                              curses.color_pair(3))
            elif grid[y][x] == 0:
                stdscr.addstr(y, x * 2, '  ')
            elif grid[y][x] >= 100:
                idx = (grid[y][x] - 100 + rainbow_offset) % 12
                stdscr.addstr(y, x * 2, '  ',
                              curses.color_pair(7 + idx))
            else:
                stdscr.addstr(y, x * 2, '  ',
                              curses.color_pair(5))


def play_fog_of_war(stdscr: curses.window,
                    maze: Maze,
                    config: dict[str, Any]) -> None:
    """Play mode with fog of war - reveals maze as player moves."""
    entry: tuple[int, int] = config['ENTRY']
    exit_pos: tuple[int, int] = config['EXIT']
    player_x: int = entry[0]
    player_y: int = entry[1]
    exit_x: int = exit_pos[0]
    exit_y: int = exit_pos[1]
    visible: set[tuple[int, int]] = set()
    radius = 2

    safe_path_str = bfs(maze.grid, entry, exit_pos)
    safe_cells: set[tuple[int, int]] = {entry, exit_pos}
    if safe_path_str:
        px: int = entry[0]
        py: int = entry[1]
        safe_cells.add((px, py))
        for letter in safe_path_str:
            if letter == 'N':
                py -= 1
            elif letter == 'S':
                py += 1
            elif letter == 'E':
                px += 1
            elif letter == 'W':
                px -= 1
            safe_cells.add((px, py))

    bombs: set[tuple[int, int]] = set()
    width: int = config['WIDTH']
    height: int = config['HEIGHT']
    nb_bombs = (width * height) // 10
    attempts = 0
    while len(bombs) < nb_bombs and attempts < nb_bombs * 20:
        attempts += 1
        bx = random.randint(0, width - 1)
        by = random.randint(0, height - 1)
        if (bx, by) not in safe_cells and (bx, by) not in bombs:
            bombs.add((bx, by))

    def reveal(px: int, py: int) -> None:
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = px + dx, py + dy
                if maze.is_valid(nx, ny):
                    visible.add((nx, ny))

    # Menu d'intro animé centré
    h, w = stdscr.getmaxyx()
    intro_lines = [
        "🌫️  Welcome to Fog of War!",
        "⬆️ ⬇️ ⬅️ ➡️  Use arrow keys to move",
        "💥  Avoid hidden bombs!",
        "🚪  Reach the exit to win!",
    ]
    stdscr.clear()
    intro_y = h // 2 - len(intro_lines) // 2
    for i, line in enumerate(intro_lines):
        x_pos = (w - len(line)) // 2
        stdscr.addstr(intro_y + i, x_pos, line)
        enter_text = "[ Press Enter to continue... ]"
        stdscr.addstr(intro_y + len(intro_lines) + 1,
                      (w - len(enter_text)) // 2, enter_text)
        stdscr.refresh()
        key = stdscr.getch()
        if key != 10:
            break

    curses.init_color(40, 200, 200, 250)
    curses.init_pair(19, 40, curses.COLOR_BLACK)
    stdscr.timeout(-1)

    seen_bombs: set[tuple[int, int]] = set()
    flash_bombs: set[tuple[int, int]] = set()

    def detect_bombs(px: int, py: int) -> None:
        for bx, by in bombs:
            if (bx, by) in seen_bombs:
                continue
            if abs(bx - px) <= radius and abs(by - py) <= radius:
                flash_bombs.add((bx, by))
                seen_bombs.add((bx, by))

    trail: set[tuple[int, int]] = set()

    reveal(player_x, player_y)
    detect_bombs(player_x, player_y)
    game_over = False

    while True:
        stdscr.clear()
        grid = create_grid(maze.grid)
        create_gallery(maze.grid, grid, True)

        for y in range(len(grid)):
            for x in range(len(grid[0])):
                is_border = (
                    x == 0 or y == 0
                    or x == 2 * maze.width
                    or y == 2 * maze.height
                )
                cell_x = min(x // 2, maze.width - 1)
                cell_y = min(y // 2, maze.height - 1)
                if is_border and grid[y][x] != 0:
                    stdscr.addstr(y, x * 2, "  ",
                                  curses.color_pair(5))
                elif grid[y][x] == 2:
                    stdscr.addstr(y, x * 2, "  ",
                                  curses.color_pair(1))
                elif (x == exit_x * 2 + 1
                      and y == exit_y * 2 + 1):
                    stdscr.addstr(y, x * 2, "  ",
                                  curses.color_pair(3))
                elif (cell_x, cell_y) not in visible:
                    stdscr.addstr(y, x * 2, "░░",
                                  curses.color_pair(19))
                elif (x == (cell_x) * 2 + 1
                      and y == (cell_y) * 2 + 1
                      and (cell_x, cell_y) in flash_bombs):
                    stdscr.addstr(y, x * 2, "💥")
                elif x == player_x * 2 + 1 and y == player_y * 2 + 1:
                    stdscr.addstr(y, x * 2, "  ", curses.color_pair(6))
                elif grid[y][x] == 0:
                    if (x, y) in trail:
                        stdscr.addstr(y, x * 2, "  ",
                                      curses.color_pair(5))
                    else:
                        stdscr.addstr(y, x * 2, "  ")
                else:
                    stdscr.addstr(y, x * 2, "  ", curses.color_pair(5))

        rules_y = 2 * height + 2
        if game_over:
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            boom = "💥 💥 💥 💥 💥 💥 💥"
            msg = "  BOOM! Game over!"
            enter = "[ Press Enter to continue... ]"
            stdscr.addstr(h // 2 - 2, (w - len(boom)) // 2, boom,
                          curses.A_BOLD)
            stdscr.addstr(h // 2, (w - len(msg)) // 2, msg, curses.A_BOLD)
            stdscr.addstr(h // 2 + 2, (w - len(boom)) // 2, boom,
                          curses.A_BOLD)
            stdscr.addstr(h // 2 + 4, (w - len(enter)) // 2, enter)
            stdscr.refresh()
            while stdscr.getch() != 10:
                pass
            break
        else:
            stdscr.addstr(rules_y, 0, "=== Fog of War ===", curses.A_BOLD)
            stdscr.addstr(rules_y + 1, 0, "⬆️ ⬇️ ⬅️ ➡️  Arrow keys to move")
            stdscr.addstr(rules_y + 2, 0, "💥  Watch out for hidden bombs!")
            stdscr.addstr(rules_y + 3, 0, "ESC or Q: return to menu")

        stdscr.refresh()
        flash_bombs.clear()
        key = stdscr.getch()

        ox = 2 * player_x + 1
        oy = 2 * player_y + 1
        if key == curses.KEY_UP and maze.can_move(
                player_x, player_y, NORTH):
            trail.add((ox, oy))
            trail.add((ox, oy - 1))
            player_y -= 1
            reveal(player_x, player_y)
            detect_bombs(player_x, player_y)
        elif key == curses.KEY_DOWN and maze.can_move(
                player_x, player_y, SOUTH):
            trail.add((ox, oy))
            trail.add((ox, oy + 1))
            player_y += 1
            reveal(player_x, player_y)
            detect_bombs(player_x, player_y)
        elif key == curses.KEY_RIGHT and maze.can_move(
                player_x, player_y, EAST):
            trail.add((ox, oy))
            trail.add((ox + 1, oy))
            player_x += 1
            reveal(player_x, player_y)
            detect_bombs(player_x, player_y)
        elif key == curses.KEY_LEFT and maze.can_move(
                player_x, player_y, WEST):
            trail.add((ox, oy))
            trail.add((ox - 1, oy))
            player_x -= 1
            reveal(player_x, player_y)
            detect_bombs(player_x, player_y)
        elif key == 27 or key == ord('q') or key == ord('Q'):
            break

        if (player_x, player_y) in bombs:
            game_over = True
            continue

        if player_x == exit_x and player_y == exit_y:
            for cy in range(maze.height):
                for cx in range(maze.width):
                    visible.add((cx, cy))
            trail.clear()
            stdscr.clear()
            grid = create_grid(maze.grid)
            create_gallery(maze.grid, grid, True)
            for y in range(len(grid)):
                for x in range(len(grid[0])):
                    if grid[y][x] == 2:
                        stdscr.addstr(y, x * 2, "  ",
                                      curses.color_pair(1))
                    elif grid[y][x] == 0:
                        stdscr.addstr(y, x * 2, "  ")
                    else:
                        stdscr.addstr(y, x * 2, "  ",
                                      curses.color_pair(5))
            win = "🎉 Congrats, you won!"
            enter = "[ Press Enter to continue... ]"
            stdscr.addstr(rules_y, 0, win, curses.A_BOLD)
            stdscr.addstr(rules_y + 1, 0, enter)
            stdscr.refresh()
            while stdscr.getch() != 10:
                pass
            break

    stdscr.timeout(150)

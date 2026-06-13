#!/usr/bin/env python3

from parser import parse_config, check_config
from maze import Maze
from bfs import bfs
from export import write_output
import curses
import random
import sys
from typing import Any
from maze_display import create_grid, create_gallery
from maze_display import display_path, display_grid
from maze_display import play_fog_of_war, animate_generation


def main(stdscr: curses.window,
         config: dict[str, Any]) -> None:
    """Main function, handles the maze display and user interactions."""
    show_path = False
    show_42 = True

    color_index = 0
    wall_colors = [curses.COLOR_WHITE, 12,
                   13, 8, 9]

    color_42_index = 0
    colors_42 = [
        curses.COLOR_MAGENTA,
        curses.COLOR_CYAN,
        curses.COLOR_GREEN,
        curses.COLOR_RED,
        curses.COLOR_YELLOW,
    ]

    curses.start_color()
    curses.use_default_colors()

    term_h, term_w = stdscr.getmaxyx()
    need_h = 2 * config['HEIGHT'] + 2 + 10
    need_w = (2 * config['WIDTH'] + 1) * 2
    if term_h < need_h or term_w < need_w:
        raise curses.error('terminal too small')

    curses.init_color(8, 1000, 200, 600)
    curses.init_color(9, 600, 400, 1000)
    curses.init_color(10, 900, 500, 700)
    curses.init_color(12, 1000, 950, 600)
    curses.init_color(13, 820, 770, 670)

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(3, curses.COLOR_WHITE, 10)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_WHITE)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_RED)  # joueur

    palettes: list[list[tuple[int, int, int]]] = [
        [   # Rainbow
            (1000, 0, 0), (1000, 400, 0), (1000, 700, 0),
            (1000, 1000, 0), (500, 1000, 0), (0, 1000, 0),
            (0, 1000, 500), (0, 1000, 1000), (0, 500, 1000),
            (0, 0, 1000), (500, 0, 1000), (1000, 0, 800),
        ],
        [   # Rose
            (1000, 200, 400), (1000, 300, 500),
            (1000, 400, 600), (1000, 500, 700),
            (1000, 600, 750), (1000, 700, 800),
            (1000, 800, 850), (1000, 700, 800),
            (1000, 600, 750), (1000, 500, 700),
            (1000, 400, 600), (1000, 300, 500),
        ],
        [   # Bleu
            (0, 100, 500), (0, 200, 600),
            (0, 300, 700), (0, 400, 800),
            (0, 500, 900), (0, 600, 1000),
            (200, 700, 1000), (400, 800, 1000),
            (200, 700, 1000), (0, 600, 1000),
            (0, 500, 900), (0, 400, 800),
        ],
    ]
    palette_names = ['Rainbow', 'Rose', 'Blue']
    palette_index = 0

    def apply_palette(idx: int) -> None:
        for i, (r, g, b) in enumerate(palettes[idx]):
            curses.init_color(20 + i, r, g, b)
            curses.init_pair(7 + i, curses.COLOR_BLACK, 20 + i)

    apply_palette(0)

    maze = Maze(
        config['WIDTH'],
        config['HEIGHT'],
        config['ENTRY'],
        config['EXIT']
    )
    seed = config.get('SEED', random.randint(0, 999999))
    animate_generation(stdscr, maze, seed, config)
    if not config['PERFECT']:
        maze.make_imperfect((config['WIDTH'] * config['HEIGHT']) // 7)
    path = bfs(maze.grid, config['ENTRY'], config['EXIT'])
    if path:
        write_output(maze.grid, config['ENTRY'], config['EXIT'],
                     path, config['OUTPUT_FILE'])

    rainbow_offset = 0
    stdscr.timeout(150)

    while True:
        try:
            stdscr.clear()
            grid = create_grid(maze.grid)
            create_gallery(maze.grid, grid, show_42)

            if show_path and path:
                display_path(grid, path, config['ENTRY'])
                rainbow_offset -= 1

            display_grid(stdscr, grid, config['ENTRY'],
                         config['EXIT'], show_42, rainbow_offset)

            menu_y = 2 * config['HEIGHT'] + 2
            mode = "Perfect" if config['PERFECT'] else "Imperfect"
            stdscr.addstr(menu_y, 0,
                          "=== A-maze-ing Menu ===",
                          curses.A_BOLD)
            stdscr.addstr(menu_y + 1, 0, "1: Regenerate maze")
            stdscr.addstr(
                menu_y + 2, 0,
                f"2: Toggle perfect/imperfect ({mode})"
            )
            stdscr.addstr(menu_y + 3, 0,
                          "3: Change wall color")
            stdscr.addstr(menu_y + 4, 0,
                          "4: Change 42 color")
            stdscr.addstr(menu_y + 5, 0,
                          "5: Show/hide shortest path")
            stdscr.addstr(
                menu_y + 6, 0,
                f"6: Change path color "
                f"({palette_names[palette_index]})"
            )
            stdscr.addstr(menu_y + 7, 0,
                          "7: Play (Fog of War)")
            stdscr.addstr(menu_y + 8, 0, "Q: Quit")
            stdscr.refresh()
        except curses.error:
            stdscr.clear()
            stdscr.addstr(0, 0, 'Terminal too small, '
                          'please resize...')
            stdscr.refresh()
        key = stdscr.getch()
        if key == -1:
            continue

        if key == ord('1'):
            seed = random.randint(0, 999999)
            maze = Maze(config['WIDTH'], config['HEIGHT'],
                        config['ENTRY'], config['EXIT'])
            animate_generation(stdscr, maze, seed, config)
            if not config['PERFECT']:
                maze.make_imperfect(
                    (config['WIDTH'] * config['HEIGHT']) // 7)
            path = bfs(maze.grid, config['ENTRY'],
                       config['EXIT'])

        elif key == ord('2'):
            config['PERFECT'] = not config['PERFECT']
            seed = random.randint(0, 999999)
            maze = Maze(config['WIDTH'], config['HEIGHT'],
                        config['ENTRY'], config['EXIT'])
            animate_generation(stdscr, maze, seed, config)
            if not config['PERFECT']:
                maze.make_imperfect(
                    (config['WIDTH'] * config['HEIGHT']) // 7)
            path = bfs(maze.grid, config['ENTRY'],
                       config['EXIT'])

        elif key == ord('3'):
            color_index = (color_index + 1) % len(wall_colors)
            curses.init_pair(5, wall_colors[color_index],
                             wall_colors[color_index])

        elif key == ord('4'):
            color_42_index += 1
            if color_42_index > len(colors_42):
                color_42_index = 0
            if color_42_index == len(colors_42):
                show_42 = False
            else:
                show_42 = True
                curses.init_pair(
                    1, curses.COLOR_BLACK,
                    colors_42[color_42_index]
                )

        elif key == ord('5'):
            show_path = not show_path

        elif key == ord('6'):
            palette_index = (palette_index + 1) % len(palettes)
            apply_palette(palette_index)

        elif key == ord('7'):
            play_fog_of_war(stdscr, maze, config)

        elif key == ord('q') or key == ord('Q'):
            break

    if path:
        write_output(maze.grid, config['ENTRY'], config['EXIT'],
                     path, config['OUTPUT_FILE'])


if __name__ == '__main__':
    raw_config = parse_config()
    config = check_config(raw_config)

    if config['WIDTH'] > 200 or config['HEIGHT'] > 100:
        print('Error: maze too large to display '
              '(max 200x100)')
        sys.exit(1)

    if (config['WIDTH'] > Maze.PATTERN_42_WIDTH + 1
            and config['HEIGHT'] > Maze.PATTERN_42_HEIGHT + 1):
        pattern = set(
            Maze(config['WIDTH'], config['HEIGHT'],
                 config['ENTRY'], config['EXIT'])
            .get_pattern_42()
        )
        if config['ENTRY'] in pattern:
            print('Error: ENTRY is inside the 42 pattern')
            sys.exit(1)
        if config['EXIT'] in pattern:
            print('Error: EXIT is inside the 42 pattern')
            sys.exit(1)

    try:
        curses.wrapper(main, config)
    except curses.error:
        print('Error: terminal window too small for this maze size')
    except KeyboardInterrupt:
        pass

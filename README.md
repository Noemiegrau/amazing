*This project has been created as part of the 42 curriculum by jerecaba, nograu.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python. It reads a configuration file, generates a maze (optionally perfect), writes it to a file using hexadecimal wall encoding, and provides an ASCII terminal visualization with user interactions.

The program supports:
- Perfect mazes (exactly one path between any two cells)
- Imperfect mazes (multiple paths, with corridor width constraint)
- A visible "42" pattern drawn with fully closed cells
- Seed-based reproducibility
- Shortest path solving using BFS
- Animated maze generation (step-by-step DFS visualization)
- Fog of War game mode
- Animated rainbow path with multiple color palettes

## Instructions

### Requirements

- Python 3.10+
- Poetry (dependency manager)

### Installation

```bash
make install
```

### Usage

```bash
make run
```

Or with a custom configuration file:

```bash
python3 a_maze_ing.py your_config.txt
```

### Linting

```bash
make lint
```

### Building the reusable package

```bash
cd mazegen/
pip install build
python -m build
```

## Configuration file

The configuration file uses `KEY=VALUE` format, one pair per line. Lines starting with `#` are comments. Keys are case-insensitive.

| Key | Type | Required | Description | Example |
|-----|------|----------|-------------|---------|
| WIDTH | integer | Yes | Maze width (number of cells) | `WIDTH=20` |
| HEIGHT | integer | Yes | Maze height (number of cells) | `HEIGHT=15` |
| ENTRY | x,y | Yes | Entry coordinates | `ENTRY=0,0` |
| EXIT | x,y | Yes | Exit coordinates | `EXIT=19,14` |
| OUTPUT_FILE | string | Yes | Output filename | `OUTPUT_FILE=maze.txt` |
| PERFECT | True/False | Yes | Generate a perfect maze | `PERFECT=True` |
| SEED | integer | No | Random seed for reproducibility | `SEED=42` |

Example configuration file:

```
# Maze configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

## Maze generation algorithm

### Chosen algorithm: Recursive Backtracker (DFS)

The maze is generated using a Recursive Backtracker algorithm, which is a depth-first search (DFS) approach.

### How it works

1. Start from a random cell, mark it as visited, push it to the stack
2. While the stack is not empty:
   - Look at the current cell's unvisited neighbors
   - If there are unvisited neighbors: pick one at random, remove the wall between them, move to it
   - If there are none: backtrack (pop the stack)

### Why this algorithm

- It naturally produces **perfect mazes** (spanning trees with no cycles)
- Simple to implement and understand
- Generates mazes with long corridors and few dead ends, which are visually appealing
- Easy to make reproducible with a seed (`random.seed()`)

### Imperfect mode

When `PERFECT=False`, additional walls are randomly opened after the initial generation. Each wall opening is validated against the 3x3 constraint to prevent large open areas.

### 42 pattern

The "42" pattern is placed at the center of the maze before generation. The cells forming the pattern are marked as visited, so the algorithm never opens their walls. They remain fully closed (`0xF`).

### Corridor width constraint

The maze cannot have open areas larger than 2 cells wide. Before opening a wall in imperfect mode, all 3x3 blocks containing the affected cells are checked. If any block would become fully open, the wall opening is cancelled.

## Reusable module: mazegen

The maze generation logic is available as a standalone Python package.

### Installation

```bash
pip install mazegen-0.1.0.tar.gz
```

### Usage

```python
from mazegen.maze import Maze

# Create a maze
maze = Maze(width=20, height=15, entry=(0, 0), exit=(19, 14))

# Generate with a seed
maze.generate(seed=42)

# Access the grid (list of lists of int, each cell 0-15)
print(maze.grid)

# Get hex representation
print(maze.to_hex())

# Check walls
maze.has_wall(0, 0, 1)   # has north wall?
maze.can_move(0, 0, 2)   # can move east?

# Find shortest path from entry to exit
path = maze.solve()       # returns 'SSEEENN...' or None

# Make imperfect (open extra walls)
maze.make_imperfect(30)
```

### Parameters

- `width` (int): maze width in cells
- `height` (int): maze height in cells
- `entry` (tuple[int, int]): entry coordinates (x, y)
- `exit` (tuple[int, int]): exit coordinates (x, y)
- `seed` (int): random seed for `generate()`

### Accessing the structure

- `maze.grid`: the raw grid as `list[list[int]]`, accessible via `grid[y][x]`
- Each cell is an integer 0-15, where bits encode closed walls: bit 0=North, bit 1=East, bit 2=South, bit 3=West

## Interactive menu

The program provides an interactive curses-based menu:

| Key | Action |
|-----|--------|
| 1 | Regenerate maze (with animation) |
| 2 | Toggle perfect/imperfect mode |
| 3 | Change wall color |
| 4 | Change 42 pattern color (cycle: magenta, cyan, green, red, yellow, off) |
| 5 | Show/hide shortest path |
| 6 | Change path color palette (Rainbow, Rose, Blue) |
| 7 | Play Fog of War |
| Q | Quit |

## Bonus features

### Animated generation

Every maze generation (startup, regenerate, toggle mode) shows the DFS algorithm building the maze step by step. The current cell is highlighted in green. Press ESC to skip the animation.

### Fog of War game mode

A game mode where the player navigates the maze with limited visibility:
- **Visibility radius**: only nearby cells are revealed
- **Fog texture**: undiscovered areas are shown as `░░`
- **Bombs**: randomly placed (avoiding the solution path), flash once when detected nearby
- **Trail camouflage**: visited cells take the wall color, making backtracking harder
- **Borders, exit and 42 pattern** are always visible
- **Win condition**: reach the exit to reveal the full maze

### Animated rainbow path

The shortest path is displayed with an animated color gradient that flows from entry to exit. Three palettes are available: Rainbow (12 vivid colors), Rose (pink gradient) and Blue (blue gradient).

### 42 pattern color cycling

The 42 pattern color can be changed interactively, cycling through magenta, cyan, green, red, yellow, and off.

### Live perfect/imperfect toggle

Switch between perfect and imperfect maze modes on the fly. The maze is regenerated with animation each time, allowing direct visual comparison of both modes.

## Resources

- [Python 3 documentation](https://docs.python.org/3/)
- [random module](https://docs.python.org/3/library/random.html) — seed, choice, randint
- [collections.deque](https://docs.python.org/3/library/collections.html#collections.deque) — used for BFS queue
- [curses module](https://docs.python.org/3/library/curses.html) — terminal-based visualization
- [Python packaging guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/) — building the mazegen package
- [Maze generation algorithms - Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Breadth-First Search - Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Spanning tree - Wikipedia](https://en.wikipedia.org/wiki/Spanning_tree) — link between perfect mazes and graph theory

### AI usage

AI was occasionally used to:
- Clarify algorithmic concepts (graph theory, DFS)
- Debug specific error messages
- Review code structure

All code was written and understood by the team members.

## Team and project management

### Team members

| Member | Role |
|--------|------|
| jerecaba (Jérémy) | Config parser, maze generation, algorithm design |
| nograu (Noémie) | Visualization, BFS, hex export, mazegen package |

### Planning

The project was split into parallel workstreams to avoid blocking each other:

1. **Foundations (together)** — Agreed on data structure (grid as `list[list[int]]`, walls as bits), class interface (~10 methods), and project setup (Poetry, Makefile, Git workflow)
2. **Parallel work:**
   - jerecaba: config parser, maze generation algorithm, seed/reproducibility, "42" pattern, 3x3 constraint, imperfect mode
   - nograu: ASCII visualization with curses, BFS shortest path, hex export, interactive menu, mazegen package
3. **Integration (together)** — Connected all modules, ran flake8/mypy, tested edge cases, wrote documentation

The key decision was to define the `Maze` class interface upfront so both could work independently. This avoided merge conflicts and allowed parallel progress.

### What worked well

- Defining the Maze class interface together before splitting the work — avoided conflicts
- Parallel workstreams — no blocking between team members
- Bitwise encoding — compact and efficient wall representation
- Using a shared Notion for planning and tracking progress

### What could be improved

- Better communication on shared files (import issues during integration)
- Starting flake8/mypy earlier instead of fixing everything at the end
- The "42" pattern took several iterations to get right — should have tested visually sooner
- Time estimates were sometimes off (generation took longer than expected)

### Tools used

- Python 3.10+
- Poetry (dependency management)
- flake8 + mypy (linting and type checking)
- Git (version control)
- Notion (project planning and knowledge base)

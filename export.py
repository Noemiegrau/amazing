#!/usr/bin/env python3

from typing import List


def write_output(maze: List[List[int]],
                 entry: tuple[int, int],
                 exit: tuple[int, int],
                 path: str,
                 filename: str) -> None:
    """Write maze hex data, entry/exit coords and path to file."""
    try:
        with open(filename, 'w') as f:
            for line in maze:
                f.write(''.join(f'{cell:X}' for cell in line) + '\n')
            f.write('\n')
            f.write(f'{entry[0]},{entry[1]}\n')
            f.write(f'{exit[0]},{exit[1]}\n')
            f.write(path + '\n')
    except OSError as e:
        print(f'Error: cannot write to {filename}: {e}')

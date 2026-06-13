from enum import Enum
import sys
from typing import Any


class KeyConfig(Enum):
    WIDTH = 'WIDTH'
    HEIGHT = 'HEIGHT'
    ENTRY = 'ENTRY'
    EXIT = 'EXIT'
    OUTPUT_FILE = 'OUTPUT_FILE'
    PERFECT = 'PERFECT'


def parse_config() -> dict[str, str]:

    if len(sys.argv) != 2:
        print('Error: program need configuration file')
        print('Please retry')
        print('example: python3 a_maze_ing.py config.txt')
        sys.exit(1)

    try:
        with open(sys.argv[1]) as file:
            config: dict[str, str] = {}
            valid_key: list[str] = [key.value for key in KeyConfig]
            valid_key.append('SEED')
            for line in file:
                line = line.strip()
                if not line.startswith('#') and len(line):
                    parts = line.split('=', 1)
                    if len(parts) != 2:
                        print(f'Error: invalid format for {parts[0]}')
                        sys.exit(1)
                    if parts[0].upper() in valid_key:
                        config[parts[0].upper()] = parts[1]
            return config

    except FileNotFoundError:
        print('Error: File Not Found')
        sys.exit(1)


def check_config(config: dict[str, str]) -> dict[str, Any]:
    valid_key: list[str] = [key.value for key in KeyConfig]
    for vk in valid_key:
        if vk not in config:
            print(f'Error: {vk} is missing from the configuration file.')
            sys.exit(1)

    new_config: dict[str, Any] = {}

    for key in ['WIDTH', 'HEIGHT']:
        try:
            value: int = int(config[key])
            if value <= 0:
                print(f'Error: {key} must be greater than 0')
                sys.exit(1)
            new_config[key] = value
        except ValueError:
            print(f'Error: {key} must be integer')
            sys.exit(1)

    for key in ['ENTRY', 'EXIT']:
        try:
            tab: list[str] = config[key].split(',')
            if len(tab) != 2:
                print(f'Error: {key} must contain two parameters')
                sys.exit(1)
            x = int(tab[0])
            y = int(tab[1])
            if not (0 <= x < new_config['WIDTH']):
                print(
                    "Error: X must be between 0 "
                    f"and ({new_config['WIDTH'] - 1})"
                    )
                sys.exit(1)
            if not (0 <= y < new_config['HEIGHT']):
                print(
                    "Error: Y must be between 0 "
                    f"and ({new_config['HEIGHT'] - 1})"
                    )
                sys.exit(1)
            new_config[key] = (x, y)
        except ValueError:
            print(f'Error: {key} must contain two integer parameters')
            sys.exit(1)

    if new_config['ENTRY'] == new_config['EXIT']:
        print('Error: ENTRY and EXIT must be different')
        sys.exit(1)

    if config['PERFECT'] not in ['True', 'False']:
        print('Error: PERFECT must be a boolean')
        sys.exit(1)
    new_config['PERFECT'] = config['PERFECT'] == 'True'

    new_config['OUTPUT_FILE'] = config['OUTPUT_FILE']

    if 'SEED' in config:
        try:
            new_config['SEED'] = int(config['SEED'])
        except ValueError:
            print('Error: SEED must be a integer parameter')
            sys.exit(1)

    return new_config

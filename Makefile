CONFIG ?= config.txt

install:
	poetry install

run:
	poetry run python3 a_maze_ing.py $(CONFIG)

debug:
	poetry run python3 -m pdb a_maze_ing.py $(CONFIG)

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +

lint:
	poetry run flake8 .
	poetry run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	poetry run flake8 .
	poetry run mypy . --strict

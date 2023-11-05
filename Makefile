PROJECT=stable_discord
SOURCE_OBJECTS=app stable_discord


format.ruff:
	poetry run ruff format ${SOURCE_OBJECTS}

format.ruff.check:
	poetry run ruff format --check ${SOURCE_OBJECTS}

format: format.ruff

lint.ruff:
	poetry run ruff check ${SOURCE_OBJECTS} --fix

lint.ruff.check:
	poetry run ruff check ${SOURCE_OBJECTS}

lint: lint.ruff

check:
	format.ruff.check
	lint.ruff.check

setup:
	python3 -m pip install poetry
	poetry install

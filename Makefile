PROJECT=stably_discordant_server
SOURCE_OBJECTS=app stably_discordant_server


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

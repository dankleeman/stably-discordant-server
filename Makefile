PROJECT=stably_discordant_server
SOURCE_OBJECTS=app stably_discordant_server

format.check:
	poetry run ruff format --check ${SOURCE_OBJECTS}

format:
	poetry run ruff format ${SOURCE_OBJECTS}

lint.check:
	poetry run ruff check ${SOURCE_OBJECTS}

lint:
	poetry run ruff check ${SOURCE_OBJECTS} --fix

type:
	poetry run mypy ${SOURCE_OBJECTS}

check: format.check lint.check type

setup:
	python3 -m pip install poetry
	poetry install

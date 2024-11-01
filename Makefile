SHELL:=/bin/bash
PACKAGE_NAME:=ksec
ROOT_DIR:=$(shell dirname $(shell pwd))

test:
	uv run pytest

mypy:
	uv run mypy ${PACKAGE_NAME} --pretty

lint:
	uv run ruff check ${PACKAGE_NAME} tests

qa: mypy lint
	echo "All quality checks pass!"

format:
	uv run ruff check --fix ${PACKAGE_NAME} tests
	uv run ruff format ${PACKAGE_NAME} tests

clean: clean-eggs clean-build
	@find . -iname '*.pyc' -delete
	@find . -iname '*.pyo' -delete
	@find . -iname '*~' -delete
	@find . -iname '*.swp' -delete
	@find . -iname '__pycache__' -delete
	@rm -r .mypy_cache
	@rm -r .pytest_cache

clean-eggs:
	@find . -name '*.egg' -print0|xargs -0 rm -rf --
	@rm -rf .eggs/

clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info

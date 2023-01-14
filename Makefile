install:
	pip install --upgrade pip
	pip install -r frozen-requirements.txt
	pre-commit install

start:
	python src/app.py

test:
	pytest tests

freeze:
	pip freeze > frozen-requirements.txt

setup-env:
	python3 -m venv .venv

pre-commit:
	pre-commit run --all-files

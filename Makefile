install:
	pip install --upgrade pip
	pip install -r frozen-requirements.txt

start:
	python src/app.py

test:
	pytest tests

freeze:
	pip freeze > frozen-requirements.txt

setup_env:
	python3 -m venv .venv

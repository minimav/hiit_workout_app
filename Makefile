.PHONY: build help
.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies in the current Python environment and install pre-commits
	pip install --upgrade pip
	pip install -r frozen-requirements.txt
	pre-commit install

start-dev:  ## Start the app using local source code
	python src/app.py

start:  ## Start the app using a built version (mac-only)
	open -n ./dist/app/app --args AppCommandLineArg

test:  ## Run the unit tests
	pytest tests

freeze:  ## Create frozen, pinned requirements from the current Python environment
	pip freeze > frozen-requirements.txt

setup-env:  ## Create a new Python virtual environment called 'venv' in ./.venv
	python3 -m venv .venv

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

build:  ## Build the app as an executable (mac-only)
	# see this link for why the first --add-date option is needed
	# https://github.com/TomSchimansky/CustomTkinter/wiki/Packaging#windows-pyinstaller-auto-py-to-exe
	# see this link for why the second two --add-data options are needed
	# https://stackoverflow.com/questions/53587322/how-do-i-include-files-with-pyinstaller
	pyinstaller \
	    --clean \
	    --noconfirm \
	    --onedir \
		--windowed \
		--add-data $$(pip show customtkinter | grep Location | cut -d " " -f2)/customtkinter:customtkinter/ \
		--add-data="src/data/*.json:src/data" \
		--add-data="src/assets/*.png:src/assets" \
		--add-data="src/assets/*.jpeg:src/assets" \
		--add-data="src/assets/*.mp3:src/assets" \
		src/app.py

gitmoji:  ## Count gitmojis per commit
	git log --oneline | grep -o -e ':.*:' | sort | uniq -c | sort -nr

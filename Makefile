.PHONY: build

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

build:
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
		src/app.py

gitmoji:
	git log --oneline | grep -o -e ':.*:' | sort | uniq -c | sort -nr

# HIIT app

This is a simple Tkinter app to help with HIIT/Kettlebell workouts. Possible exercises are stored in `exercises.json` and can be modified as desired. Saved workouts can be defined in `workouts.json` and loaded, or randomised workouts with custom durations used.

## Installation

First, create a virtual environment with your preferred Python version (>=3.9):

```bash
python -m venv .venv
source .venv/bin/activate
```

Then run `make install` to install requirements and setup pre-commit hooks.

## Usage

Either `python src/app.py` or `make start`.

## Tests

Either `pytest tests` or `make test`.

## Todo

* Able to add new exercises
* Able to save workouts

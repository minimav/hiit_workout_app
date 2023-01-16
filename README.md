# HIIT app

![test workflow](https://github.com/minimav/hiit_workout_app/actions/workflows/test.yaml/badge.svg)

This is a simple Tkinter app to help with HIIT/Kettlebell workouts. Possible exercises are stored in `src/data/exercises.json` and can be modified as desired. Saved workouts can be defined in `src/data/workouts.json` and loaded, or randomised workouts with custom durations used.

Here is an example of a custom workout whose exercises have been randomly selected:

![workout](media/app.gif)

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

## Building

To build the app as an exe or equivalent for your OS, run `make build`. The resulting artefact will be in the `dist` folder.

## Repo stats

[Gitmoji](https://gitmoji.dev/) stats via `make gitmoji`:

* 7 :memo:
* 6 :sparkles:
* 5 :recycle:
* 4 :bug:
* 3 :white_check_mark:
* 3 :technologist:
* 3 :construction_worker:
* 2 :test_tube:
* 2 :see_no_evil:
* 2 :rotating_light:
* 2 :heavy_plus_sign:
* 2 :children_crossing:
* 2 :adhesive_bandage:
* 1 :wrench:
* 1 :twisted_rightwards_arrows:
* 1 :tada:
* 1 :recycle: :white_check_mark:
* 1 :pushpin:
* 1 :pencil2:
* 1 :label:
* 1 :bento:

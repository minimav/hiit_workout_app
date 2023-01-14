import json
import sys

import pytest

sys.path.append("src")

from exercise import ExerciseManager  # noqa: E402
from workout import WorkoutManager  # noqa: E402


@pytest.fixture(scope="function")
def exercise_manager(tmpdir) -> ExerciseManager:
    """Create exercise manager with simple exercise set and temp file."""
    exercises = {
        "1-handed-exercise": {"single_handed_variations": True},
        "2-handed-exercise": {"single_handed_variations": False},
    }
    path = tmpdir / "exercises.json"
    with open(path, "w") as f:
        json.dump(exercises, f)

    return ExerciseManager(path=path)


@pytest.fixture(scope="function")
def workout_manager(tmpdir) -> WorkoutManager:
    """Create workout manager with simple workouts and temp file."""
    workouts = {
        "workout-1": {
            "exercise_duration_seconds": 40,
            "rest_duration_seconds": 20,
            "exercises": [
                "1-handed-exercise",
                "1-handed-exercise",
            ],
        },
        "workout-2": {
            "exercise_duration_seconds": 10,
            "rest_duration_seconds": 10,
            "exercises": [
                "1-handed-exercise",
                "2-handed-exercise",
            ],
        },
    }
    path = tmpdir / "workouts.json"
    with open(path, "w") as f:
        json.dump(workouts, f)

    return WorkoutManager(path=path)

import sys

sys.path.append("src")

import json

import pytest

from exercise import ExerciseManager


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

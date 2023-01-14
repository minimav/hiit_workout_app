import json
import sys

import pytest

sys.path.append("src")

from exercise import ExerciseManager  # noqa: E402


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

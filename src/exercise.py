"""Functions and structs for creating workouts."""
from dataclasses import dataclass
from pathlib import Path
import json


from utils import get_path_to_file


@dataclass
class Exercise:
    """An exercise, either 2-handed or with 1-handed variations."""

    name: str
    single_handed_variations: bool


@dataclass
class Rest:
    """A rest between exercises"""

    pass


class ExerciseManager:
    """Manages available exercises."""

    def __init__(
        self,
        path: Path = Path("src") / "exercises.json",
    ):
        self.path = get_path_to_file(path)
        self.exercises = self.load_exercises()

    def __len__(self) -> int:
        return len(self.exercises)

    def __getitem__(self, exercise_name: str) -> Exercise:
        return self.exercises[exercise_name]

    def __iter__(self):
        return iter(self.exercises.items())

    def load_exercises(self) -> dict[str, Exercise]:
        """Load all possible exercises."""
        exercises = {}
        with open(self.path, "r") as f:
            for exercise_name, metadata in json.load(f).items():
                exercises[exercise_name] = Exercise(
                    exercise_name, metadata["single_handed_variations"]
                )
        return exercises

    def add_exercise(self, exercise: Exercise):
        """Add an exercise to the library of all exercises."""
        self.exercises[exercise.name] = exercise

        with open(self.path, "r") as f:
            exercises = json.load(f)

        exercises[exercise.name] = {
            "single_handed_variations": exercise.single_handed_variations
        }
        with open(self.path, "w") as f:
            json.dump(exercises, f)

    def remove_exercise(self, exercise_name: str):
        """Remove an exercise from the library of all exercises."""
        del self.exercises[exercise_name]

        with open(self.path, "r") as f:
            exercises = json.load(f)

        del exercises[exercise_name]
        with open(self.path, "w") as f:
            json.dump(exercises, f)

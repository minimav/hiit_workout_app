"""Functions and structs for creating workouts."""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict
import json


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
    """In control of available exercises."""

    path: Path = Path("src") / "exercises.json"

    def __init__(self):
        self.exercises = self.load_exercises()

    def __len__(self) -> int:
        return len(self.exercises)

    @classmethod
    def load_exercises(cls) -> Dict[str, Exercise]:
        """Load all possible exercises."""
        exercises = {}
        with open(cls.path, "r") as f:
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

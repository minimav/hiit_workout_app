"""Functions and structs for creating workouts."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import random

from exercise import Exercise, ExerciseManager, Rest
from utils import get_path_to_file


@dataclass
class Phase:
    """A workout phase, either an exercise or a rest."""

    duration_seconds: int
    type: Exercise | Rest


Workout = list[Phase]


@dataclass
class WorkoutConfig:
    """Config for a stored workout."""

    exercise_duration_seconds: int
    rest_duration_seconds: int
    exercises: list[str]

    def calculate_num_exercises(self, exercise_manager: ExerciseManager) -> int:
        """Get # exercises in workout, taking 1-handed variants into account."""
        num_exercises = 0
        for exercise_name in self.exercises:
            exercise = exercise_manager[exercise_name]
            if exercise.single_handed_variations:
                num_exercises += 2
            else:
                num_exercises += 1
        return num_exercises


class WorkoutManager:
    """Manages stored workouts and creating them."""

    def __init__(
        self,
        path: Path = Path("src") / "workouts.json",
    ):
        self.path = get_path_to_file(path)
        self.workouts = self.load_workouts()

    def __len__(self):
        return len(self.workouts)

    def __getitem__(self, workout_name: str) -> WorkoutConfig:
        return self.workouts[workout_name]

    def __iter__(self):
        return iter(self.workouts.items())

    def load_workouts(self) -> dict[str, WorkoutConfig]:
        """Load previously stored workouts."""
        with open(self.path, "r") as f:
            return {k: WorkoutConfig(**v) for k, v in json.load(f).items()}

    def add_workout(self, workout_name: str, config: WorkoutConfig):
        """Add (or update) a new saved workout."""
        self.workouts[workout_name] = config

        with open(self.path, "r") as f:
            workouts = json.load(f)

        workouts[workout_name] = asdict(config)
        with open(self.path, "w") as f:
            json.dump(workouts, f)

    def remove_workout(self, workout_name: str):
        """Remove a stored workout."""
        del self.workouts[workout_name]

        with open(self.path, "r") as f:
            workouts = json.load(f)

        del workouts[workout_name]
        with open(self.path, "w") as f:
            json.dump(workouts, f)

    @property
    def exercises_in_workouts(self) -> set[str]:
        """Get all exercises which appear in any saved workout"""
        exercises = set()
        for workout in self.workouts.values():
            exercises.update(workout.exercises)
        return exercises


def apply_workout_correction(workout: Workout) -> Workout:
    """Apply correction for going over limit via 1-handed variations.

    This could happen for example if we were generating a workout with 4
    exercises but during generation sampled 2 exercises with 1-handed
    variations and a 2-handed exercise, for 5 exercises in total. Removing
    the 2-handed exercise -- if ones exists -- fixes this.

    This function assumes that a check has already been done on the number
    of exercises to ensure that the correction is needed.
    """
    for index, phase in enumerate(workout):
        if isinstance(phase.type, Exercise) and not phase.type.single_handed_variations:
            # remove first 2-handed exercise and preceding rest
            return workout[: index - 1] + workout[index + 1 :]

    # edge case where odd number of exercises but all 1-handed variants chosen
    # so we fail in the check above - in this case just do the 1-minute longer
    # workout!
    return workout


def generate_workout(
    exercise_manager: ExerciseManager,
    num_exercises: int,
    exercise_duration_seconds: int = 5,
    rest_duration_seconds: int = 3,
    allow_repeats: bool = False,
) -> Workout:
    """Generate a workout with desired # of exercises."""
    exercise_names = list(exercise_manager.exercises.keys())

    if not allow_repeats:
        assert num_exercises < len(exercise_manager)

    rest_phase = Phase(rest_duration_seconds, Rest())
    already_done = set()
    workout: Workout = []
    while len(workout) < 2 * num_exercises:
        exercise = exercise_manager[random.choice(exercise_names)]
        if exercise.name in already_done:
            continue
        if not allow_repeats:
            already_done.add(exercise.name)

        if exercise.single_handed_variations:
            for side in ("left", "right"):
                one_sided_exercise = Exercise(f"{exercise.name} ({side})", True)
                workout.append(rest_phase)
                workout.append(Phase(exercise_duration_seconds, one_sided_exercise))
        else:
            workout.append(rest_phase)
            workout.append(Phase(exercise_duration_seconds, exercise))

    if len(workout) > 2 * num_exercises:
        return apply_workout_correction(workout)

    return workout


def workout_from_config(
    exercise_manager: ExerciseManager, config: WorkoutConfig
) -> Workout:
    """Create a workout from config."""
    rest_phase = Phase(config.rest_duration_seconds, Rest())
    workout = []
    for exercise_name in config.exercises:
        exercise = exercise_manager[exercise_name]

        if exercise.single_handed_variations:
            for side in ("left", "right"):
                one_sided_exercise = Exercise(f"{exercise.name} ({side})", True)
                workout.append(rest_phase)
                workout.append(
                    Phase(config.exercise_duration_seconds, one_sided_exercise)
                )
        else:
            workout.append(rest_phase)
            workout.append(Phase(config.exercise_duration_seconds, exercise))
    return workout

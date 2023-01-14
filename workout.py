"""Functions and structs for creating workouts."""
from dataclasses import dataclass
from typing import Dict, List, Union
import json
import random


@dataclass
class Exercise:
    """An exercise, either 2-handed or with 1-handed variations."""

    name: str
    single_handed_variations: bool


@dataclass
class Rest:
    """A rest between exercises"""

    pass


@dataclass
class Phase:
    """A workout phase, either an exercise or a rest."""

    duration_seconds: int
    type: Union[Exercise, Rest]


Workout = List[Phase]


@dataclass
class WorkoutConfig:
    """Config for a stored workout."""

    exercise_duration_seconds: int
    rest_duration_seconds: int
    exercises: List[str]

    def calculate_num_exercises(self) -> int:
        """Get # exercises in workout, taking 1-handed variants into account."""
        num_exercises = 0
        for exercise_name in self.exercises:
            exercise = EXERCISES[exercise_name]
            if exercise.single_handed_variations:
                num_exercises += 2
            else:
                num_exercises += 1
        return num_exercises


def load_exercises() -> Dict[str, Exercise]:
    """Load all possible exercises."""
    exercises = {}
    with open("exercises.json", "r") as f:
        for exercise_name, metadata in json.load(f).items():
            exercises[exercise_name] = Exercise(
                exercise_name, metadata["single_handed_variations"]
            )
    return exercises


EXERCISES = load_exercises()


def load_workouts() -> Dict[str, WorkoutConfig]:
    """Load previously stored workouts."""
    with open("workouts.json", "r") as f:
        return {k: WorkoutConfig(**v) for k, v in json.load(f).items()}


def generate_workout(
    num_exercises: int,
    exercise_duration_seconds: int = 5,
    rest_duration_seconds: int = 3,
    allow_repeats: bool = False,
) -> Workout:
    """Generate a workout with desired # of exercises."""
    exercise_names = list(EXERCISES.keys())

    if not allow_repeats:
        assert num_exercises < len(EXERCISES)

    rest_phase = Phase(rest_duration_seconds, Rest())
    already_done = set()
    workout = []
    while len(workout) < 2 * num_exercises:
        exercise = EXERCISES[random.choice(exercise_names)]
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
        # apply correction for going over limit with 1-handed variations
        for index, phase in enumerate(workout):
            if (
                isinstance(phase.type, Exercise)
                and not phase.type.single_handed_variations
            ):
                # remove first 2-handed exercise and preceding rest
                return workout[: index - 1] + workout[index + 1 :]

        # edge case where odd number of exercises but all 1-handed variants chosen
        # so we fail in the check above - in this case just do the 1-minute longer
        # workout!

    return workout


def workout_from_config(config: WorkoutConfig) -> Workout:
    """Create a workout from config."""
    rest_phase = Phase(config.rest_duration_seconds, Rest())
    workout = []
    for exercise_name in config.exercises:
        workout.append(rest_phase)
        exercise = EXERCISES[exercise_name]

        if exercise.single_handed_variations:
            for side in ("left", "right"):
                one_sided_exercise = Exercise(f"{exercise.name} ({side})", True)
                workout.append(
                    Phase(config.exercise_duration_seconds, one_sided_exercise)
                )
        else:
            workout.append(Phase(config.exercise_duration_seconds, exercise))
    return workout

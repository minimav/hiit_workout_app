"""Tests for workout module."""
import pytest

from exercise import Exercise, Rest
from workout import apply_workout_correction, Phase, WorkoutConfig, WorkoutManager


def test_apply_workout_correction():
    """Incorrect length workouts should be truncated correctly.

    This workout could arise if a workout with 4 exercises was generated
    with 2 exercises with 1-handed variations sampled along with a
    2-handed exercise. Note that in this scenario the 2-handed exercise
    could not be the last one sampled, otherwise the generation would
    terminate with the correct number of 4 exercises from the 2 exercises
    with 1-handed variations.
    """
    fixed_duration_seconds = 10
    rest_phase = Phase(fixed_duration_seconds, Rest())
    workout = [
        rest_phase,
        Phase(fixed_duration_seconds, Exercise("name (left)", True)),
        rest_phase,
        Phase(fixed_duration_seconds, Exercise("name (right)", True)),
        rest_phase,
        Phase(fixed_duration_seconds, Exercise("removed", False)),
        rest_phase,
        Phase(fixed_duration_seconds, Exercise("name (left)", True)),
        rest_phase,
        Phase(fixed_duration_seconds, Exercise("name (right)", True)),
    ]

    corrected_workout = apply_workout_correction(workout)
    assert len(corrected_workout) == 8
    assert all(
        phase.type.name != "removed"
        for phase in corrected_workout
        if isinstance(phase.type, Exercise)
    )


def test_no_workout_correction_applied():
    """Edge case cannot be corrected, so workout remains the same.

    This workout could arise if a workout with 1 exercise was generated
    and the first exercise sampled was one with 1-handed variations.
    """
    fixed_duration_seconds = 10
    rest_phase = Phase(fixed_duration_seconds, Rest())
    workout = [
        rest_phase,
        Phase(fixed_duration_seconds, Exercise("name (left)", True)),
        rest_phase,
        Phase(fixed_duration_seconds, Exercise("name (right)", True)),
    ]

    corrected_workout = apply_workout_correction(workout)
    assert corrected_workout == workout


@pytest.mark.parametrize(
    "exercises, expected_num_exercises",
    [
        (["2-handed-exercise"], 1),
        (["1-handed-exercise"], 2),
        (["1-handed-exercise", "1-handed-exercise"], 4),
        (["2-handed-exercise", "2-handed-exercise"], 2),
        (["2-handed-exercise", "1-handed-exercise"], 3),
    ],
)
def test_calculate_num_exercises(exercises, expected_num_exercises, exercise_manager):
    """Total # of exercises is correct, taking into account 1-handed variants."""
    config = WorkoutConfig(
        exercise_duration_seconds=10, rest_duration_seconds=10, exercises=exercises
    )
    assert config.calculate_num_exercises(exercise_manager) == expected_num_exercises


def test_add_workout(workout_manager):
    """A workout should be added correctly."""
    num_exercises = 10
    workout_name = "new-workout"
    config = WorkoutConfig(
        exercise_duration_seconds=30,
        rest_duration_seconds=30,
        exercises=["1-handed-exercise"] * num_exercises,
    )
    current_num_workouts = len(workout_manager)
    workout_manager.add_workout(workout_name, config)

    # new workout should be reflected for new workout manager pointing
    # at the same path as well as the one we interacted with to add
    new_workout_manager = WorkoutManager(path=workout_manager.path)
    for manager in (workout_manager, new_workout_manager):
        assert current_num_workouts + 1 == len(manager)
        assert workout_name in manager.workouts
        assert len(manager[workout_name].exercises) == num_exercises


def test_update_workout(workout_manager):
    """A workout should be updated correctly."""
    num_exercises = 10
    workout_name = "workout-1"
    config = WorkoutConfig(
        exercise_duration_seconds=30,
        rest_duration_seconds=30,
        exercises=["2-handed-exercise"] * num_exercises,
    )
    current_num_workouts = len(workout_manager)
    workout_manager.add_workout(workout_name, config)

    # new workout should be reflected for new workout manager pointing
    # at the same path as well as the one we interacted with to add
    new_workout_manager = WorkoutManager(path=workout_manager.path)
    for manager in (workout_manager, new_workout_manager):
        assert current_num_workouts == len(manager)
        assert workout_name in manager.workouts
        assert manager[workout_name] == config


@pytest.mark.parametrize("workout_name", ["workout-1", "workout-2"])
def test_remove_workout(workout_manager, workout_name):
    """A workout should be removed correctly."""
    current_num_workouts = len(workout_manager)
    workout_manager.remove_workout(workout_name)

    # removal should be reflected for new workout manager pointing
    # at the same path as well as the one we interacted with to remove
    new_workout_manager = WorkoutManager(path=workout_manager.path)
    for manager in (workout_manager, new_workout_manager):
        assert current_num_workouts - 1 == len(manager)
        assert workout_name not in manager.workouts

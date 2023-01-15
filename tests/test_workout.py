"""Tests for workout module."""
from hypothesis import given, HealthCheck, settings
from hypothesis.strategies import data, integers, lists, sampled_from
import pytest

from exercise import Exercise, Rest
from workout import (
    apply_workout_correction,
    generate_workout,
    Phase,
    workout_from_config,
    Workout,
    WorkoutConfig,
    WorkoutManager,
)


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


def test_exercises_in_workouts(workout_manager):
    """Exercises in workouts should be retrieved correctly."""
    # only first two are in a workout to begin with
    all_exercises = [
        "1-handed-exercise",
        "2-handed-exercise",
        "another-exercise",
    ]
    workout_manager.exercises = all_exercises
    assert workout_manager.exercises_in_workouts == {
        "1-handed-exercise",
        "2-handed-exercise",
    }

    # add workout that uses the other exercise
    config = WorkoutConfig(
        exercise_duration_seconds=30,
        rest_duration_seconds=30,
        exercises=["another-exercise"],
    )
    workout_manager.add_workout("new-workout", config)
    # now all exercises should be in a workout
    assert workout_manager.exercises_in_workouts == set(all_exercises)


def validate_rest_exercise_interleaving(workout: Workout):
    """Check that rests and exercises are interleaved correctly."""
    assert all(
        isinstance(phase.type, Rest) for i, phase in enumerate(workout) if i % 2 == 0
    )
    assert all(
        isinstance(phase.type, Exercise)
        for i, phase in enumerate(workout)
        if i % 2 == 1
    )


@settings(suppress_health_check=(HealthCheck.function_scoped_fixture,))
@given(
    num_exercises=integers(min_value=2, max_value=30),
    exercise_duration_seconds=integers(min_value=1, max_value=30),
    rest_duration_seconds=integers(min_value=1, max_value=30),
)
def test_generate_workout_has_rests_in_between_exercises(
    exercise_manager_with_more_exercises,
    num_exercises,
    exercise_duration_seconds,
    rest_duration_seconds,
):
    """A generated workout should have rests interleaved with the exercises."""
    workout = generate_workout(
        exercise_manager_with_more_exercises,
        num_exercises=num_exercises,
        exercise_duration_seconds=exercise_duration_seconds,
        rest_duration_seconds=rest_duration_seconds,
        allow_repeats=False,
    )
    validate_rest_exercise_interleaving(workout)
    all_single_handed = all(
        phase.type.single_handed_variations
        for phase in workout
        if isinstance(phase.type, Exercise)
    )
    if all_single_handed and num_exercises % 2 == 1:
        # edge case where correction to remove a 2-handed exercise can't be applied
        # thus we end up with one rest and one exercise phase too many
        assert len(workout) == 2 * num_exercises + 2
    else:
        assert len(workout) == 2 * num_exercises


@settings(suppress_health_check=(HealthCheck.function_scoped_fixture,))
@given(
    data=data(),
    num_exercises=integers(min_value=1, max_value=30),
    exercise_duration_seconds=integers(min_value=1, max_value=30),
    rest_duration_seconds=integers(min_value=1, max_value=30),
)
def test_workout_from_config_has_rests_in_between_exercises(
    exercise_manager_with_more_exercises,
    data,
    num_exercises,
    exercise_duration_seconds,
    rest_duration_seconds,
):
    """A workout made from config should have rests interleaved with the exercises."""
    all_exercises = list(exercise_manager_with_more_exercises.exercises.keys())
    workout_config = WorkoutConfig(
        exercise_duration_seconds=exercise_duration_seconds,
        rest_duration_seconds=rest_duration_seconds,
        exercises=data.draw(
            lists(
                sampled_from(all_exercises),
                min_size=num_exercises,
                max_size=num_exercises,
            )
        ),
    )
    workout = workout_from_config(exercise_manager_with_more_exercises, workout_config)
    print()
    print(workout)
    validate_rest_exercise_interleaving(workout)

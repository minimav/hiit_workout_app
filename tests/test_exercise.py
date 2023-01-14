"""Tests for the exercise module."""
import pytest

from exercise import Exercise, ExerciseManager


@pytest.mark.parametrize(
    "exercise",
    [Exercise("new-1-handed-exercise", True), Exercise("new-2-handed-exercise", False)],
)
def test_add_exercise(exercise_manager, exercise):
    """An exercise should be added to the library correctly."""
    current_num_exercises = len(exercise_manager)
    exercise_manager.add_exercise(exercise)

    # new exercise should be reflected for new exercise manager pointing
    # at the same path as well as the one we interacted with to add
    new_exercise_manager = ExerciseManager(path=exercise_manager.path)
    for manager in (exercise_manager, new_exercise_manager):
        assert current_num_exercises + 1 == len(manager)
        assert exercise.name in manager.exercises
        assert (
            manager.exercises[exercise.name].single_handed_variations
            == exercise.single_handed_variations
        )


@pytest.mark.parametrize(
    "exercise",
    [Exercise("1-handed-exercise", True), Exercise("2-handed-exercise", False)],
)
def test_remove_exercise(exercise_manager, exercise):
    """An exercise should be removed from the library correctly."""
    current_num_exercises = len(exercise_manager)
    exercise_manager.remove_exercise(exercise.name)

    # removal should be reflected for new exercise manager pointing
    # at the same path as well as the one we interacted with to remove
    new_exercise_manager = ExerciseManager(path=exercise_manager.path)
    for manager in (exercise_manager, new_exercise_manager):
        assert current_num_exercises - 1 == len(manager)
        assert exercise.name not in manager.exercises

"""Module for GUI window to edit exercises."""
import customtkinter
import tkinter

from exercise import Exercise, ExerciseManager


class ExerciseEditor:
    """Window that allows editing exercises."""

    def __init__(
        self, parent, exercise_manager: ExerciseManager, exercises_in_workouts: set[str]
    ):
        self.window = customtkinter.CTkToplevel(parent)
        self.window.title("Edit exercises")
        self.exercise_manager = exercise_manager
        self.exercises_in_workouts = exercises_in_workouts
        self.window.geometry("400x400")

        self.add_exercise_label = customtkinter.CTkLabel(
            self.window, text="Add exercise", font=("roboto", 24)
        )
        self.add_exercise_label.pack(side="top", fill="both", padx=10, pady=10)

        self.new_exercise_name = customtkinter.CTkTextbox(self.window, height=20)
        self.new_exercise_name.insert("0.0", "Exercise name")
        self.new_exercise_name.pack(side="top", padx=10, pady=10)

        self.new_exercise_has_single_handed_variations = tkinter.BooleanVar()
        self.single_handed_checkbox = customtkinter.CTkCheckBox(
            master=self.window,
            text="Has 1-handed variations",
            variable=self.new_exercise_has_single_handed_variations,
        )
        self.single_handed_checkbox.pack(padx=20, pady=10)

        self.add_exercise_button = customtkinter.CTkButton(
            master=self.window, command=self.add_exercise, text="Add"
        )
        self.add_exercise_button.pack(padx=10, pady=10)

        self.remove_exercise_label = customtkinter.CTkLabel(
            self.window, text="Remove exercise", font=("roboto", 24)
        )
        self.remove_exercise_label.pack(side="top", fill="both", padx=10, pady=10)

        self.exercises_dropdown = customtkinter.CTkOptionMenu(
            master=self.window, values=list(self.exercise_manager.exercises.keys())
        )
        self.exercises_dropdown.pack(padx=10, pady=10)

        self.remove_exercise_button = customtkinter.CTkButton(
            master=self.window, command=self.remove_exercise, text="Remove"
        )
        self.remove_exercise_button.pack(padx=10, pady=10)

    def update_exercises_dropdown(self):
        """Update the exercises in the dropdown for removal."""
        values = list(self.exercise_manager.exercises.keys())
        self.exercises_dropdown.set(values[0])
        self.exercises_dropdown.configure(values=values)

    def add_exercise(self):
        """Add an exercise."""
        exercise_name = self.new_exercise_name.get("0.0", "end").rstrip()
        has_single_handed_variations = (
            self.new_exercise_has_single_handed_variations.get()
        )
        exercise = Exercise(exercise_name, has_single_handed_variations)
        self.exercise_manager.add_exercise(exercise)
        self.new_exercise_name.delete("0.0", "end")
        self.update_exercises_dropdown()

    def remove_exercise(self):
        """Remove an exercise."""
        to_remove = self.exercises_dropdown.get()
        if to_remove not in self.exercises_in_workouts:
            self.exercise_manager.remove_exercise(to_remove)
            self.update_exercises_dropdown()

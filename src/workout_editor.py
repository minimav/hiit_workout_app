"""Module for GUI window to edit workouts."""
from typing import Callable

import customtkinter
import tkinter

from gui_components import Slider
from workout import WorkoutConfig, WorkoutManager


class WorkoutEditor:
    """Window that allows editing workouts."""

    def __init__(
        self,
        parent,
        workout_manager: WorkoutManager,
        exercises: list[str],
        on_close_callback: Callable,
    ):
        self.window = customtkinter.CTkToplevel(parent)
        self.window.title("Edit workouts")
        self.workout_manager = workout_manager
        self.exercises = exercises
        self.on_close_callback = on_close_callback
        self.window.geometry("400x600")

        def on_closing():
            on_close_callback()
            self.window.destroy()

        self.window.protocol("WM_DELETE_WINDOW", on_closing)

        self.add_workout_label = customtkinter.CTkLabel(
            self.window, text="Add workout", font=("roboto", 24)
        )
        self.add_workout_label.pack(side="top", fill="both", padx=10, pady=10)

        self.new_workout_exercises: list[str] = []
        self.new_workout_name = customtkinter.CTkTextbox(self.window, height=20)
        self.new_workout_name.insert("0.0", "Workout name")
        self.new_workout_name.pack(side="top", padx=10, pady=10)

        self.exercise_duration_seconds_slider = Slider(
            parent=self.window,
            default=40,
            from_=30,
            to=120,
            label_template="{value} seconds/exercise",
        )

        self.rest_duration_seconds_slider = Slider(
            parent=self.window,
            default=20,
            from_=10,
            to=60,
            label_template="{value} seconds/rest",
        )

        self.exercises_dropdown = customtkinter.CTkOptionMenu(
            master=self.window,
            values=self.exercises,
            command=self.add_exercise_to_workout,
        )
        self.exercises_dropdown.pack(padx=10, pady=10)

        self.new_workout_exercises_text_box = customtkinter.CTkTextbox(
            master=self.window,
            state=tkinter.DISABLED,
        )
        self.new_workout_exercises_text_box.pack(padx=10, pady=10)
        self.remove_exercise_from_workout_button = customtkinter.CTkButton(
            master=self.window,
            command=self.remove_exercise_from_workout,
            text="Remove exercise",
        )
        self.remove_exercise_from_workout_button.pack(padx=10, pady=10)

        self.add_workout_button = customtkinter.CTkButton(
            master=self.window, command=self.add_workout, text="Add"
        )
        self.add_workout_button.pack(padx=10, pady=10)

        self.remove_workout_label = customtkinter.CTkLabel(
            self.window, text="Remove workout", font=("roboto", 24)
        )
        self.remove_workout_label.pack(side="top", fill="both", padx=10, pady=10)

        self.workouts_dropdown = customtkinter.CTkOptionMenu(
            master=self.window, values=list(self.workout_manager.workouts.keys())
        )
        self.workouts_dropdown.pack(padx=10, pady=10)

        self.remove_workout_button = customtkinter.CTkButton(
            master=self.window, command=self.remove_workout, text="Remove"
        )
        self.remove_workout_button.pack(padx=10, pady=10)

    def update_workouts_dropdown(self):
        """Update the workouts in the dropdown for removal."""
        values = list(self.workout_manager.workouts.keys())
        self.workouts_dropdown.set(values[0])
        self.workouts_dropdown.configure(values=values)

    def add_workout(self):
        """Add a workout ."""
        workout_name = self.new_workout_name.get("0.0", "end").rstrip()
        config = WorkoutConfig(
            exercise_duration_seconds=self.exercise_duration_seconds_slider.value,
            rest_duration_seconds=self.rest_duration_seconds_slider.value,
            exercises=self.new_workout_exercises,
        )
        self.workout_manager.add_workout(workout_name, config)
        self.new_workout_name.delete("0.0", "end")
        self.clear_new_workout_exercises()
        self.new_workout_exercises = []
        self.update_workouts_dropdown()

    def remove_workout(self):
        """Remove a workout."""
        to_remove = self.workouts_dropdown.get()
        self.workout_manager.remove_workout(to_remove)
        self.update_workouts_dropdown()

    def add_exercise_to_workout(self, exercise_name: str):
        """Add exercise to the current workout."""
        self.new_workout_exercises.append(exercise_name)
        self.update_new_workout_exercises()

    def remove_exercise_from_workout(self):
        """Remove the last exercise from the new workout."""
        self.new_workout_exercises.pop()
        self.update_new_workout_exercises()

    def clear_new_workout_exercises(self):
        """Clear the list of exercises for the new workout."""
        self.new_workout_exercises_text_box.configure(state=tkinter.NORMAL)
        self.new_workout_exercises_text_box.delete("0.0", "end")
        self.new_workout_exercises_text_box.configure(state=tkinter.DISABLED)

    def update_new_workout_exercises(self):
        """Update the list of exercises in the new workout."""
        self.clear_new_workout_exercises()
        self.new_workout_exercises_text_box.configure(state=tkinter.NORMAL)
        self.new_workout_exercises_text_box.insert(
            "0.0", "\n".join(self.new_workout_exercises), "centered"
        )
        self.new_workout_exercises_text_box.configure(state=tkinter.DISABLED)

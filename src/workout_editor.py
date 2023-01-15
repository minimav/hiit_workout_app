"""Module for GUI window to edit workouts."""
from typing import Callable

import customtkinter

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
        self.window.geometry("400x400")

        def on_closing():
            on_close_callback()
            self.window.destroy()

        self.window.protocol("WM_DELETE_WINDOW", on_closing)

        self.add_workout_label = customtkinter.CTkLabel(
            self.window, text="Add workout", font=("roboto", 24)
        )
        self.add_workout_label.pack(side="top", fill="both", padx=10, pady=10)

        self.new_workout_name = customtkinter.CTkTextbox(self.window, height=20)
        self.new_workout_name.insert("0.0", "Workout name")
        self.new_workout_name.pack(side="top", padx=10, pady=10)

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
            exercise_duration_seconds=10,
            rest_duration_seconds=10,
            exercises=[],
        )
        self.workout_manager.add_workout(workout_name, config)
        self.new_workout_name.delete("0.0", "end")
        self.update_workouts_dropdown()

    def remove_workout(self):
        """Remove a workout."""
        to_remove = self.workouts_dropdown.get()
        self.workout_manager.remove_workout(to_remove)
        self.update_workouts_dropdown()

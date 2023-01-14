"""HIIT workout app."""
from typing import List

import tkinter
import customtkinter

from exercise import Exercise, ExerciseManager, Rest
from workout import (
    generate_workout,
    load_workouts,
    Workout,
    workout_from_config,
)


class App(customtkinter.CTk):
    """HIIT workout app main class."""

    num_exercises_default: int = 10
    exercise_duration_seconds_default: int = 30
    rest_duration_seconds_default: int = 20

    def __init__(self):
        super().__init__()

        self.exercise_manager = ExerciseManager()

        self.geometry("1000x450")
        self.title("HIIT Workout")
        self.minsize(500, 300)

        self.workouts = load_workouts()

        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.countdown = customtkinter.CTkFrame(self, corner_radius=0)
        self.countdown.grid(
            row=0, column=1, columnspan=2, padx=10, pady=10, sticky="nsew"
        )
        self.clock = customtkinter.CTkLabel(
            master=self.countdown, text="", font=("roboto", 96)
        )
        self.clock.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        self.exercise_info = customtkinter.CTkLabel(
            master=self.countdown, text="", font=("roboto", 36)
        )
        self.exercise_info.place(relx=0.5, rely=0.15, anchor=tkinter.CENTER)
        self.callbacks = []

        self.workout = customtkinter.CTkFrame(self, width=50, corner_radius=0)
        self.workout.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")

        self.options_title = customtkinter.CTkLabel(
            master=self.workout, text="Workout options", font=("roboto", 24), pady=10
        ).pack()

        self.saved_workout_dropdown = customtkinter.CTkOptionMenu(
            master=self.workout,
            values=["Custom"] + list(self.workouts.keys()),
            command=self.change_workout_type,
        )
        self.saved_workout_dropdown.pack(padx=10, pady=10)

        self.options_title = customtkinter.CTkLabel(
            master=self.workout,
            text="Customise",
            font=("roboto", 20),
            pady=10,
        ).pack()

        self.num_exercises_info = customtkinter.CTkLabel(
            master=self.workout,
            text=f"{self.num_exercises_default} exercises",
            font=("roboto", 18),
        )
        self.num_exercises_info.pack()
        self.num_exercises_slider = customtkinter.CTkSlider(
            master=self.workout,
            from_=10,
            to=30,
            number_of_steps=20,
            command=self.update_num_exercises_info,
        )
        self.num_exercises_slider.set(self.num_exercises_default)
        self.num_exercises_slider.pack(padx=10, pady=10)

        self.exercise_duration_info = customtkinter.CTkLabel(
            master=self.workout,
            text=f"{self.exercise_duration_seconds_default} seconds/exercise",
            font=("roboto", 18),
        )
        self.exercise_duration_info.pack()
        self.exercise_duration_seconds_slider = customtkinter.CTkSlider(
            master=self.workout,
            from_=30,
            to=120,
            number_of_steps=90,
            command=self.update_exercise_duration_info,
        )
        self.exercise_duration_seconds_slider.set(
            self.exercise_duration_seconds_default
        )
        self.exercise_duration_seconds_slider.pack(padx=10, pady=10)

        self.rest_duration_info = customtkinter.CTkLabel(
            master=self.workout,
            text=f"{self.rest_duration_seconds_default} seconds/rest",
            font=("roboto", 18),
        )
        self.rest_duration_info.pack()
        self.rest_duration_seconds_slider = customtkinter.CTkSlider(
            master=self.workout,
            from_=5,
            to=60,
            number_of_steps=55,
            command=self.update_rest_duration_info,
        )
        self.rest_duration_seconds_slider.set(self.rest_duration_seconds_default)
        self.rest_duration_seconds_slider.pack(padx=10, pady=10)

        self.start_workout_button = customtkinter.CTkButton(
            master=self.workout, command=self.start_workout, text="Start"
        )
        self.start_workout_button.pack(padx=10, pady=10)
        self.reset_workout_button = customtkinter.CTkButton(
            master=self.workout, command=self.reset_timer, text="Reset"
        )
        self.reset_workout_button.pack(padx=10, pady=10)

        self.exercises = customtkinter.CTkFrame(self, height=50, corner_radius=0)
        self.exercises.grid(
            row=1, column=1, columnspan=3, padx=10, pady=10, sticky="nsew"
        )
        self.exercises_title = customtkinter.CTkLabel(
            master=self.exercises,
            text="Next exercises",
            font=("roboto", 20),
            pady=10,
        ).pack()
        self.exercise_list = customtkinter.CTkLabel(master=self.exercises, text="")
        self.exercise_list.pack()

    def create_phases_for_custom_workout(self):
        """Create phases for a custom workout using selected settings."""
        num_exercises = int(self.num_exercises_slider.get())
        exercise_duration_seconds = int(self.exercise_duration_seconds_slider.get())
        rest_duration_seconds = int(self.rest_duration_seconds_slider.get())
        return generate_workout(
            self.exercise_manager,
            num_exercises,
            exercise_duration_seconds=exercise_duration_seconds,
            rest_duration_seconds=rest_duration_seconds,
        )

    def load_phases_for_saved_workout(self, workout_name: str) -> Workout:
        """Load phases that comprise a saved workout."""
        return workout_from_config(self.exercise_manager, self.workouts[workout_name])

    def start_workout(self):
        """Begin a workout.

        First we check whether to use a saved workout, where the exercise order,
        duration and order etc. are already defined, versus a custom workout where
        only durations and total number of exercises are fixed.

        Then appropriate callbacks are set to update the countdown display with
        the current progress throught the workout.

        """
        self.reset_timer()

        saved_workout_dropdown_value = self.saved_workout_dropdown._current_value
        if saved_workout_dropdown_value == "Custom":
            phases = self.create_phases_for_custom_workout()
        else:
            phases = self.load_phases_for_saved_workout(saved_workout_dropdown_value)

        num_exercises = sum(1 for phase in phases if isinstance(phase.type, Exercise))
        total_seconds = sum(phase.duration_seconds for phase in phases)

        exercises = [p.type for p in phases if isinstance(p.type, Exercise)]
        exercise_texts = [exercise.name for exercise in exercises]

        total_milliseconds = 0
        exercise_index = 0
        for phase in phases:
            is_rest = isinstance(phase.type, Rest)
            if exercise_index == 0 and is_rest:
                fg_color = "orange"
            elif is_rest:
                fg_color = "green"
            else:
                fg_color = "red"
                exercise_index += 1

            callback = self.after(
                total_milliseconds, self.set_countdown_color, fg_color
            )
            self.callbacks.append(callback)

            if isinstance(phase.type, Exercise):
                callback = self.after(
                    total_milliseconds,
                    self.update_exercise_info,
                    phase.type.name,
                    exercise_index,
                    num_exercises,
                    total_seconds,
                )
                self.callbacks.append(callback)
            else:
                callback = self.after(
                    total_milliseconds,
                    self.update_exercise_info_with_rest,
                    exercise_index,
                    num_exercises,
                )
                self.callbacks.append(callback)

                callback = self.after(
                    total_milliseconds,
                    self.update_exercise_list,
                    exercise_texts[exercise_index : exercise_index + 5],
                )
                self.callbacks.append(callback)

            for i in range(phase.duration_seconds):
                callback = self.after(
                    total_milliseconds,
                    self.update_clock,
                    phase.duration_seconds - i,
                )
                self.callbacks.append(callback)
                total_milliseconds += 1000

        self.after(total_milliseconds, lambda: self.clock.configure(text=""))
        self.after(total_milliseconds, lambda: self.exercise_info.configure(text=""))
        self.after(
            total_milliseconds, lambda: self.countdown.configure(fg_color="gray17")
        )

    def update_clock(self, seconds):
        """Update the seconds remaining during the current phase."""
        self.clock.configure(text=str(seconds))

    def update_exercise_info(
        self, exercise_name, exercise_index, num_exercises, total_seconds
    ):
        """Update information about the current exercise phase."""
        text = f"{exercise_name}\nExercise {exercise_index}/{num_exercises}"
        self.exercise_info.configure(text=text)

    def update_exercise_info_with_rest(self, exercise_index, num_exercises):
        """Update information about the current rest phase."""
        text = f"Rest\n{exercise_index}/{num_exercises} exercises completed"
        self.exercise_info.configure(text=text)

    def set_countdown_color(self, fg_color):
        """Change the countdown background colour to reflect phase type."""
        self.countdown.configure(fg_color=fg_color)

    def reset_timer(self):
        """Rest all timer/countdown information.

        This can occur if the workout is manually reset or finishes naturally.
        """
        for callback in self.callbacks:
            self.after_cancel(callback)
        self.callbacks = []
        self.exercise_info.configure(text="")
        self.clock.configure(text="")
        self.countdown.configure(fg_color="gray17")
        self.exercise_list.configure(text="")

    def update_num_exercises_info(self, value):
        """Update the custom # exercises after a slider change."""
        self.num_exercises_info.configure(text=f"{int(value)} exercises")

    def update_exercise_duration_info(self, value):
        """Update the custom per-exercise duration after a slider change."""
        self.exercise_duration_info.configure(text=f"{int(value)} seconds/exercise")

    def update_rest_duration_info(self, value):
        """Update the custom per-rest duration after a slider change."""
        self.rest_duration_info.configure(text=f"{int(value)} seconds/rest")

    def update_exercise_list(self, exercise_texts: List[str]):
        """Update the list of upcoming exercises after a phase change."""
        self.exercise_list.configure(text="\n".join(exercise_texts))

    def change_workout_type(self, workout_name):
        """Change workout type via dropdown."""
        self.saved_workout_dropdown.set(workout_name)

        # disable/enable customisation depending on type selected
        state = tkinter.NORMAL if workout_name == "Custom" else tkinter.DISABLED
        self.num_exercises_slider.configure(state=state)
        self.exercise_duration_seconds_slider.configure(state=state)
        self.rest_duration_seconds_slider.configure(state=state)

        if workout_name != "Custom":
            workout = self.workouts[workout_name]
            num_exercises = workout.calculate_num_exercises(self.exercise_manager)
            self.num_exercises_slider.set(num_exercises)
            self.update_num_exercises_info(num_exercises)
            self.exercise_duration_seconds_slider.set(workout.exercise_duration_seconds)
            self.update_exercise_duration_info(workout.exercise_duration_seconds)
            self.rest_duration_seconds_slider.set(workout.rest_duration_seconds)
            self.update_rest_duration_info(workout.rest_duration_seconds)


if __name__ == "__main__":
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue")
    app = App()
    app.mainloop()

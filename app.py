"""HIIT workout app."""

from dataclasses import dataclass
from typing import List, Union
import json
import random

import tkinter
import customtkinter


@dataclass
class Exercise:
    name: str
    has_left_right: bool


@dataclass
class Rest:
    pass


@dataclass
class Phase:
    duration_seconds: int
    type: Union[Exercise, Rest]


exercises = []
with open("exercises.json", "r") as f:
    for exercise_name, metadata in json.load(f).items():
        exercises.append(Exercise(exercise_name, metadata["has_left_right"]))


def generate_workout(
    num_exercises: int,
    exercise_duration_seconds: int = 5,
    rest_duration_seconds: int = 3,
) -> List[Phase]:
    """Generate a workout with desired # of exercises."""
    # no repeats for now
    assert num_exercises < len(exercises)
    rest_phase = Phase(rest_duration_seconds, Rest())
    already_done = set()
    workout = [rest_phase]
    while len(workout) < 2 * num_exercises:
        exercise = random.choice(exercises)
        if exercise.name in already_done:
            continue

        already_done.add(exercise_name)
        if exercise.has_left_right:
            for side in ("left", "right"):
                one_sided_exercise = Exercise(f"{exercise.name} ({side})", True)
                workout.append(Phase(exercise_duration_seconds, one_sided_exercise))
                workout.append(rest_phase)
        else:
            workout.append(Phase(exercise_duration_seconds, exercise))
            workout.append(rest_phase)

    # ignore final rest
    return workout[:-1]


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1000x600")
        self.title("HIIT Workout")
        self.minsize(500, 300)

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

        self.num_exercises_info = customtkinter.CTkLabel(
            master=self.workout, text="20 exercises", font=("roboto", 18)
        )
        self.num_exercises_info.pack()
        self.num_exercises_slider = customtkinter.CTkSlider(
            master=self.workout,
            from_=10,
            to=30,
            number_of_steps=20,
            command=self.update_num_exercises_info,
        )
        self.num_exercises_slider.set(20)
        self.num_exercises_slider.pack(padx=10, pady=10)

        self.exercise_duration_info = customtkinter.CTkLabel(
            master=self.workout, text="40 seconds/exercise", font=("roboto", 18)
        )
        self.exercise_duration_info.pack()
        self.exercise_duration_seconds_slider = customtkinter.CTkSlider(
            master=self.workout,
            from_=30,
            to=120,
            number_of_steps=90,
            command=self.update_exercise_duration_info,
        )
        self.exercise_duration_seconds_slider.set(40)
        self.exercise_duration_seconds_slider.pack(padx=10, pady=10)

        self.rest_duration_info = customtkinter.CTkLabel(
            master=self.workout, text="20 seconds/rest", font=("roboto", 18)
        )
        self.rest_duration_info.pack()
        self.rest_duration_seconds_slider = customtkinter.CTkSlider(
            master=self.workout,
            from_=5,
            to=60,
            number_of_steps=55,
            command=self.update_rest_duration_info,
        )
        self.rest_duration_seconds_slider.set(20)
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
        self.exercise_list = customtkinter.CTkLabel(master=self.exercises, text="")
        self.exercise_list.pack()

    def start_workout(self):
        """Being a workout."""
        self.reset_timer()
        num_exercises = int(self.num_exercises_slider.get())
        exercise_duration_seconds = int(self.exercise_duration_seconds_slider.get())
        rest_duration_seconds = int(self.rest_duration_seconds_slider.get())
        total_seconds = (
            num_exercises * exercise_duration_seconds
            + rest_duration_seconds * (num_exercises - 1)
        )

        phases = generate_workout(
            num_exercises,
            exercise_duration_seconds=exercise_duration_seconds,
            rest_duration_seconds=rest_duration_seconds,
        )
        exercises = [p.type for p in phases if isinstance(p.type, Exercise)]
        exercise_texts = [
            f"{i}: {exercise.name}" for i, exercise in enumerate(exercises, start=1)
        ]

        total_milliseconds = 0
        exercise_index = 0
        for phase in phases:
            if phase.type == Rest():
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
        self.clock.configure(text=str(seconds))

    def update_exercise_info(
        self, exercise_name, exercise_index, num_exercises, total_seconds
    ):
        text = f"{exercise_name}\nExercise {exercise_index}/{num_exercises}"
        self.exercise_info.configure(text=text)

    def update_exercise_info_with_rest(self, exercise_index, num_exercises):
        text = f"Rest\n{exercise_index}/{num_exercises} exercises completed"
        self.exercise_info.configure(text=text)

    def set_countdown_color(self, fg_color):
        self.countdown.configure(fg_color=fg_color)

    def reset_timer(self):
        for callback in self.callbacks:
            self.after_cancel(callback)
        self.callbacks = []
        self.exercise_info.configure(text="")
        self.clock.configure(text="")
        self.countdown.configure(fg_color="gray17")
        self.exercise_list.configure(text="")

    def update_num_exercises_info(self, value):
        self.num_exercises_info.configure(text=f"{int(value)} exercises")

    def update_exercise_duration_info(self, value):
        self.exercise_duration_info.configure(text=f"{int(value)} seconds/exercise")

    def update_rest_duration_info(self, value):
        self.rest_duration_info.configure(text=f"{int(value)} seconds/rest")

    def update_exercise_list(self, exercise_texts):
        self.exercise_list.configure(text="\n".join(exercise_texts))


if __name__ == "__main__":
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue")
    app = App()
    app.mainloop()

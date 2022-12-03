from dataclasses import dataclass
from enum import Enum

import tkinter
import customtkinter


class PhaseType(Enum):
    EXERCISE = 0
    REST = 1


@dataclass
class Phase:
    duration_seconds: int
    type: PhaseType


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
            row=0, column=1, columnspan=2, padx=10, pady=(10, 0), sticky="nsew"
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
        self.workout.grid(
            row=0, column=0, rowspan=2, padx=10, pady=(10, 0), sticky="nsew"
        )
        self.start_workout_button = customtkinter.CTkButton(
            master=self.workout, command=self.start_workout, text="Start"
        )
        self.start_workout_button.pack()
        self.reset_workout_button = customtkinter.CTkButton(
            master=self.workout, command=self.reset_timer, text="Reset"
        )
        self.reset_workout_button.pack()

        self.exercises = customtkinter.CTkFrame(self, height=50, corner_radius=0)
        self.exercises.grid(
            row=1, column=1, columnspan=3, padx=10, pady=(10, 0), sticky="nsew"
        )

    def start_workout(self):
        self.reset_timer()
        num_exercises = 2
        exercise_duration_seconds = 5
        rest_duration_seconds = 3
        total_seconds = (
            num_exercises * exercise_duration_seconds
            + rest_duration_seconds * (num_exercises - 1)
        )

        phases = []
        for exercise_phase_index in range(num_exercises):
            phases.append(Phase(exercise_duration_seconds, PhaseType.EXERCISE))
            if exercise_phase_index < num_exercises - 1:
                phases.append(Phase(rest_duration_seconds, PhaseType.REST))

        total_milliseconds = 0
        exercise_index = 0
        exercise_name = "Triceps Dips"
        for phase in phases:
            if phase.type == PhaseType.EXERCISE:
                fg_color = "red"
                exercise_index += 1
            else:
                fg_color = "green"

            callback = self.after(
                total_milliseconds, self.set_countdown_color, fg_color
            )
            self.callbacks.append(callback)

            if phase.type == PhaseType.EXERCISE:
                callback = self.after(
                    total_milliseconds,
                    self.update_exercise_info,
                    exercise_name,
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


if __name__ == "__main__":
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue")
    app = App()
    app.mainloop()

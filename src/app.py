"""HIIT workout app."""
import tkinter
import customtkinter

from exercise import Exercise, ExerciseManager, Rest
from workout import (
    generate_workout,
    Phase,
    Workout,
    WorkoutManager,
    workout_from_config,
)


class App(customtkinter.CTk):
    """HIIT workout app main class."""

    num_exercises_default: int = 10
    exercise_duration_seconds_default: int = 30
    rest_duration_seconds_default: int = 20
    num_next_exercises: int = 10

    def __init__(self, width=1000, height=500):
        super().__init__()
        self.width = width
        self.height = height

        self.geometry(f"{width}x{height}")
        self.minsize(500, 300)
        self.title("HIIT Workout")

        self.exercise_manager = ExerciseManager()
        self.workout_manager = WorkoutManager()

        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.countdown = customtkinter.CTkFrame(self, corner_radius=0)
        self.countdown.grid(
            row=0, rowspan=2, column=1, columnspan=2, padx=10, pady=10, sticky="nsew"
        )
        self.clock = customtkinter.CTkLabel(
            master=self.countdown, text="", font=("roboto", 96)
        )
        self.clock.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)
        self.exercise_info = customtkinter.CTkLabel(
            master=self.countdown, text="", font=("roboto", 36)
        )
        self.exercise_info.place(relx=0.5, rely=0.2, anchor=tkinter.CENTER)
        self.callbacks = []

        self.workout = customtkinter.CTkFrame(self, width=50, corner_radius=0)
        self.workout.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="nsew")

        self.options_title = customtkinter.CTkLabel(
            master=self.workout, text="Workout options", font=("roboto", 24), pady=10
        ).pack()

        self.saved_workout_dropdown = customtkinter.CTkOptionMenu(
            master=self.workout,
            values=["Custom"] + list(self.workout_manager.workouts.keys()),
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
        self.update_num_exercises_info(self.num_exercises_default)
        self.num_exercises_slider.pack(padx=10, pady=10)

        self.exercise_duration_info = customtkinter.CTkLabel(
            master=self.workout,
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
        self.update_exercise_duration_info(self.exercise_duration_seconds_default)
        self.exercise_duration_seconds_slider.pack(padx=10, pady=10)

        self.rest_duration_info = customtkinter.CTkLabel(
            master=self.workout,
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
        self.update_rest_duration_info(self.rest_duration_seconds_default)
        self.rest_duration_seconds_slider.pack(padx=10, pady=10)

        self.start_workout_button = customtkinter.CTkButton(
            master=self.workout, command=self.start_workout, text="Start"
        )
        self.start_workout_button.pack(padx=10, pady=10)
        self.reset_workout_button = customtkinter.CTkButton(
            master=self.workout, command=self.reset_timer, text="Reset"
        )
        self.reset_workout_button.pack(padx=10, pady=10)

        self.next_exercises_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.next_exercises_frame.grid(
            row=2, column=1, columnspan=2, padx=10, pady=10, sticky="nsew"
        )
        self.next_exercises_title = customtkinter.CTkLabel(
            master=self.next_exercises_frame,
            text="Next exercises",
            font=("roboto", 20),
            pady=10,
        ).pack()
        self.next_exercises = customtkinter.CTkTextbox(
            master=self.next_exercises_frame,
            state=tkinter.DISABLED,
            width=self.width / 3,
            fg_color="gray17",
        )
        self.next_exercises.tag_config("centered", justify="center")
        self.next_exercises.pack()

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
        return workout_from_config(
            self.exercise_manager, self.workout_manager[workout_name]
        )

    def get_phase_countdown_colour(
        self, phase: Phase, before_first_exercise: bool
    ) -> str:
        """Get colour for timer for particular type of phase.

        The initial rest period gets a different colour to distinguish it
        from rests between exercises.
        """
        is_rest = isinstance(phase.type, Rest)
        if before_first_exercise and is_rest:
            return "orange"
        elif is_rest:
            return "green"
        else:
            return "red"

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
        exercise_names = [exercise.name for exercise in exercises]

        total_milliseconds = 0
        exercise_index = 0
        for phase in phases:
            fg_color = self.get_phase_countdown_colour(
                phase, before_first_exercise=exercise_index == 0
            )
            if isinstance(phase.type, Exercise):
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
                    self.update_next_exercises,
                    exercise_names[
                        exercise_index : exercise_index + self.num_next_exercises
                    ],
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
        self.next_exercises.configure(state=tkinter.NORMAL)
        self.next_exercises.delete("0.0", "end")
        self.next_exercises.configure(state=tkinter.DISABLED)

    def update_num_exercises_info(self, value):
        """Update the # exercises after a slider change."""
        self.num_exercises_slider.set(value)
        self.num_exercises_info.configure(text=f"{int(value)} exercises")

    def update_exercise_duration_info(self, value):
        """Update the custom per-exercise duration after a slider change."""
        self.exercise_duration_seconds_slider.set(value)
        self.exercise_duration_info.configure(text=f"{int(value)} seconds/exercise")

    def update_rest_duration_info(self, value):
        """Update the custom per-rest duration after a slider change."""
        self.rest_duration_seconds_slider.set(value)
        self.rest_duration_info.configure(text=f"{int(value)} seconds/rest")

    def update_next_exercises(self, exercise_names: list[str]):
        """Update the list of upcoming exercises after a phase change."""
        self.next_exercises.configure(state=tkinter.NORMAL)
        self.next_exercises.insert("0.0", "\n".join(exercise_names), "centered")
        self.next_exercises.configure(state=tkinter.DISABLED)

    def change_workout_type(self, workout_name):
        """Change workout type via dropdown."""
        self.saved_workout_dropdown.set(workout_name)

        # disable/enable customisation depending on type selected
        state = tkinter.NORMAL if workout_name == "Custom" else tkinter.DISABLED
        self.num_exercises_slider.configure(state=state)
        self.exercise_duration_seconds_slider.configure(state=state)
        self.rest_duration_seconds_slider.configure(state=state)

        if workout_name != "Custom":
            workout = self.workout_manager[workout_name]
            num_exercises = workout.calculate_num_exercises(self.exercise_manager)
            self.update_num_exercises_info(num_exercises)
            self.update_exercise_duration_info(workout.exercise_duration_seconds)
            self.update_rest_duration_info(workout.rest_duration_seconds)


if __name__ == "__main__":
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue")
    app = App()
    app.mainloop()

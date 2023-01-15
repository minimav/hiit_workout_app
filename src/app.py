"""HIIT workout app."""
import tkinter
import customtkinter

from exercise import Exercise, ExerciseManager, Rest
from exercise_editor import ExerciseEditor
from gui_components import Slider
from workout import (
    generate_workout,
    Phase,
    Workout,
    WorkoutManager,
    workout_from_config,
)
from workout_editor import WorkoutEditor


class App(customtkinter.CTk):
    """HIIT workout app main class."""

    def __init__(self, width=1000, height=550):
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

        self.countdown = customtkinter.CTkFrame(
            self, corner_radius=0, height=2 * self.height / 3
        )
        self.countdown.grid(
            row=0, rowspan=1, column=1, columnspan=2, padx=10, pady=10, sticky="nsew"
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

        self.workout = customtkinter.CTkFrame(self, corner_radius=0)
        self.workout.grid(
            row=0,
            column=0,
            rowspan=3,
            columnspan=1,
            padx=10,
            pady=10,
            sticky="nsew",
        )

        self.options_title = customtkinter.CTkLabel(
            master=self.workout, text="Workout options", font=("roboto", 24), pady=10
        ).pack()

        self.saved_workout_dropdown = customtkinter.CTkOptionMenu(
            master=self.workout,
            command=self.change_workout_type,
        )
        self.saved_workout_dropdown.pack(padx=10, pady=10)
        self.update_saved_workouts()

        self.edit_workouts_button = customtkinter.CTkButton(
            master=self.workout, command=self.edit_workouts, text="Edit workouts"
        )
        self.edit_workouts_button.pack(padx=10, pady=10)

        self.options_title = customtkinter.CTkLabel(
            master=self.workout,
            text="Customise",
            font=("roboto", 20),
            pady=10,
        ).pack()

        self.edit_exercises_button = customtkinter.CTkButton(
            master=self.workout, command=self.edit_exercises, text="Edit exercises"
        )
        self.edit_exercises_button.pack(padx=10, pady=10)

        self.workout_option_sliders: list[Slider] = []
        self.num_exercises_slider = Slider(
            parent=self.workout,
            default=20,
            from_=10,
            to=30,
            label_template="{value} exercises",
        )
        self.workout_option_sliders.append(self.num_exercises_slider)

        self.exercise_duration_seconds_slider = Slider(
            parent=self.workout,
            default=40,
            from_=30,
            to=120,
            label_template="{value} seconds/exercise",
        )
        self.workout_option_sliders.append(self.exercise_duration_seconds_slider)

        self.rest_duration_seconds_slider = Slider(
            parent=self.workout,
            default=20,
            from_=10,
            to=60,
            label_template="{value} seconds/rest",
        )
        self.workout_option_sliders.append(self.rest_duration_seconds_slider)

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
            row=2, rowspan=1, column=1, columnspan=2, padx=10, pady=10, sticky="nsew"
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
            fg_color="gray17",
        )
        self.next_exercises.tag_config("centered", justify="center")
        self.next_exercises.pack(fill="both")

    def create_phases_for_custom_workout(self):
        """Create phases for a custom workout using selected settings."""
        return generate_workout(
            self.exercise_manager,
            num_exercises=self.num_exercises_slider.value,
            exercise_duration_seconds=self.exercise_duration_seconds_slider.value,
            rest_duration_seconds=self.rest_duration_seconds_slider.value,
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
                    exercise_names[exercise_index:],
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

    def update_saved_workouts(self):
        """Update the saved workouts dropdown."""
        values = ["Custom"] + list(self.workout_manager.workouts.keys())
        self.saved_workout_dropdown.set(values[0])
        self.saved_workout_dropdown.configure(values=values)

    def update_next_exercises(self, exercise_names: list[str]):
        """Update the list of upcoming exercises after a phase change."""
        self.next_exercises.configure(state=tkinter.NORMAL)
        self.next_exercises.insert("0.0", "\n".join(exercise_names), "centered")
        self.next_exercises.configure(state=tkinter.DISABLED)

    def change_workout_type(self, workout_name):
        """Change workout type via dropdown."""
        self.saved_workout_dropdown.set(workout_name)

        # disable/enable customisation depending on type selected
        if workout_name != "Custom":
            for slider in self.workout_option_sliders:
                slider.disable()
        else:
            for slider in self.workout_option_sliders:
                slider.enable()

        if workout_name != "Custom":
            workout = self.workout_manager[workout_name]
            num_exercises = workout.calculate_num_exercises(self.exercise_manager)
            self.num_exercises_slider.update(num_exercises)
            self.exercise_duration_seconds_slider.update(
                workout.exercise_duration_seconds
            )
            self.rest_duration_seconds_slider.update(workout.rest_duration_seconds)

    def edit_workouts(self):
        """Pane for adding or removing workouts."""
        exercises = list(self.exercise_manager.exercises.keys())
        WorkoutEditor(
            parent=self,
            workout_manager=self.workout_manager,
            exercises=exercises,
            on_close_callback=self.update_saved_workouts,
        )

    def edit_exercises(self):
        """Pane for adding or removing exercises."""
        exercises_in_workouts = set()
        for _, workout in self.workout_manager:
            exercises_in_workouts.update(workout.exercises)
        ExerciseEditor(
            parent=self,
            exercise_manager=self.exercise_manager,
            exercises_in_workouts=exercises_in_workouts,
        )


if __name__ == "__main__":
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue")
    app = App()
    app.mainloop()

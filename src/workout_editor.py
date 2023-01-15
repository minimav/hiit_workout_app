"""Module for GUI window to edit workouts."""
import customtkinter


class WorkoutEditor:
    """Window that allows editing workouts."""

    def __init__(self, parent, workout_manager, on_close_callback):
        self.window = customtkinter.CTkToplevel(parent)
        self.window.title("Edit workouts")
        self.workout_manager = workout_manager
        self.on_close_callback = on_close_callback
        self.window.geometry("400x400")

        label = customtkinter.CTkLabel(self.window, text="placeholder")
        label.pack(side="top", fill="both", expand=True, padx=40, pady=40)

        def on_closing():
            on_close_callback()
            self.window.destroy()

        self.window.protocol("WM_DELETE_WINDOW", on_closing)

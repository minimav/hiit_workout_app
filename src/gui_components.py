"""Resuable GUI components."""
from typing import Optional

import customtkinter
import tkinter


class Slider:
    """Resuable slider component."""

    def __init__(
        self,
        parent,
        default: int,
        from_: int,
        to: int,
        label_template: str,
        number_of_steps: Optional[int] = None,
    ):
        self.parent = parent
        self.default = default
        self.label_template = label_template
        self.label = customtkinter.CTkLabel(
            master=self.parent,
            font=("roboto", 18),
        )
        self.label.pack()

        if number_of_steps is None:
            number_of_steps = to - from_
        self.slider = customtkinter.CTkSlider(
            master=self.parent,
            from_=from_,
            to=to,
            number_of_steps=number_of_steps,
            command=self.update,
        )
        self.update(self.default)
        self.slider.pack(padx=10, pady=10)

    def update(self, value):
        """Update the custom per-rest duration after a slider change."""
        value = int(value)
        self.slider.set(value)
        self.label.configure(text=self.label_template.format(value=value))

    @property
    def value(self) -> int:
        """Get the current value of the slider"""
        return int(self.slider.get())

    def enable(self):
        """Enable this slider and go back to default colours."""
        self.slider.configure(
            state=tkinter.NORMAL,
            progress_color=("gray40", "#AAB0B5"),
            button_color=("#3B8ED0", "#1F6AA5"),
            button_hover_color=("#36719F", "#144870"),
        )

    def disable(self):
        """Disable this slider and grey-out to visually indicate."""
        self.slider.configure(
            state=tkinter.DISABLED,
            progress_color="gray",
            button_color="gray",
            button_hover_color="gray",
        )

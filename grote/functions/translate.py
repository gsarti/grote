from time import localtime, strftime
from typing import Any

import gradio as gr


def set_start_time_fn(state: dict[str, Any]) -> None:
    state["start_time"] = strftime("%d %b %Y %H:%M:%S", localtime())
    gr.Info("Ready to translate!\nStart time: " + state["start_time"])
    return state


def record_textbox_focus_fn(state: dict[str, Any], textbox: str) -> None:
    state["focused_textbox"] = textbox
    gr.Info("Focused textbox: " + state["focused_textbox"])
    print(state)
    return state


def record_textbox_input_fn(state: dict[str, Any], textbox: gr.components.Textbox) -> None:
    state["focused_textbox"] = textbox
    gr.Info("Inputted textbox: " + state["focused_textbox"])
    print(state)
    return state


def record_textbox_blur_fn(state: dict[str, Any], textbox: gr.components.Textbox) -> None:
    state["focused_textbox"] = textbox
    gr.Info("Blurred textbox: " + state["focused_textbox"])
    print(state)
    return state

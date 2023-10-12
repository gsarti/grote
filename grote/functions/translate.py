from time import localtime, strftime
from typing import Any

import gradio as gr


def set_start_time_fn(state: dict[str, Any]) -> None:
    state["start_time"] = strftime("%d %b %Y %H:%M:%S", localtime())
    gr.Info("Ready to translate!\nStart time: " + state["start_time"])
    return state

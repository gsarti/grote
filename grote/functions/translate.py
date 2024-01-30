from datetime import datetime
from pprint import pprint
from typing import Any

import gradio as gr
from gradio_highlightedtextbox import HighlightedTextbox

from grote.collections.base import COMPONENT_CONFIGS

TRANS_CFG = COMPONENT_CONFIGS["translate"]


def get_current_time() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def set_start_time_fn(state: dict[str, Any]) -> None:
    state["start_time"] = get_current_time()
    gr.Info("Ready to translate!\nStart time: " + state["start_time"])
    return state


def record_textbox_focus_fn(state: dict[str, Any], textbox_content: dict, lc_state: dict[str, Any]) -> None:
    out = {
        "time": get_current_time(),
        "user_id": lc_state["login_code_txt"],
        "text_id": textbox_content["id"],
        "type": "enter",
    }
    if textbox_content["id"] not in state:
        state[textbox_content["id"]] = {}
        state[textbox_content["id"]]["events"] = []
    if "current_text" not in state[textbox_content["id"]]:
        state[textbox_content["id"]]["current_text"] = ""
    state[textbox_content["id"]]["events"].append(out)
    state["events"].append(out)
    gr.Info(f"Entered textbox {textbox_content['id']}")
    pprint(out)
    return state


def record_textbox_input_fn(state: dict[str, Any], textbox_content: dict, lc_state: dict[str, Any]) -> None:
    current_text = HighlightedTextbox.tuples_to_tagged_text(textbox_content["data"], TRANS_CFG["highlight_label"])
    if textbox_content["id"] not in state:
        state[textbox_content["id"]] = {}
        state[textbox_content["id"]]["events"] = []
    if "current_text" not in state[textbox_content["id"]]:
        state[textbox_content["id"]]["current_text"] = current_text
    if current_text:
        if current_text != state[textbox_content["id"]]["current_text"]:
            out = {
                "time": get_current_time(),
                "user_id": lc_state["login_code_txt"],
                "text_id": textbox_content["id"],
                "type": "change",
                "text": current_text,
            }
            state[textbox_content["id"]]["current_text"] = current_text
            state[textbox_content["id"]]["events"].append(out)
            state["events"].append(out)
            gr.Info(f"Changed textbox {textbox_content['id']}: " + current_text)
            pprint(out)
    return state


def record_textbox_blur_fn(state: dict[str, Any], textbox_content: dict, lc_state: dict[str, Any]) -> None:
    out = {
        "time": get_current_time(),
        "user_id": lc_state["login_code_txt"],
        "text_id": textbox_content["id"],
        "type": "exit",
    }
    if textbox_content["id"] not in state:
        state[textbox_content["id"]] = {}
        state[textbox_content["id"]]["events"] = []
    state[textbox_content["id"]]["events"].append(out)
    state["events"].append(out)
    gr.Info(f"Exited textbox {textbox_content['id']}")
    pprint(out)
    return state

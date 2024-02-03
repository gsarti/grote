from datetime import datetime
from typing import Any

from grote.collections.base import COMPONENT_CONFIGS

TRANS_CFG = COMPONENT_CONFIGS["translate"]


def get_current_time() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def record_trial_start_fn(state: dict[str, Any], lc_state: dict[str, Any]) -> dict[str, Any]:
    out = {
        "time": get_current_time(),
        "login_code": lc_state["login_code_txt"],
        "event_type": "start",
    }
    state["events"].append(out)
    return state


def record_textbox_focus_fn(state: dict[str, Any], textbox_content: dict, lc_state: dict[str, Any]) -> dict[str, Any]:
    out = {
        "time": get_current_time(),
        "login_code": lc_state["login_code_txt"],
        "text_id": textbox_content["id"],
        "event_type": "enter",
    }
    state["events"].append(out)
    return state


def record_textbox_input_fn(state: dict[str, Any], textbox_content: dict, lc_state: dict[str, Any]) -> dict[str, Any]:
    current_text = "".join(
        f"<h>{text}</h>" if tag_id is not None else text for text, tag_id in textbox_content["data"]
    )
    if textbox_content["id"] not in state or current_text != state[textbox_content["id"]]:
        out = {
            "time": get_current_time(),
            "login_code": lc_state["login_code_txt"],
            "text_id": textbox_content["id"],
            "event_type": "change",
            "text": current_text,
        }
        state[textbox_content["id"]] = current_text
        state["events"].append(out)
    return state


def record_textbox_blur_fn(state: dict[str, Any], textbox_content: dict, lc_state: dict[str, Any]) -> dict[str, Any]:
    out = {
        "time": get_current_time(),
        "login_code": lc_state["login_code_txt"],
        "text_id": textbox_content["id"],
        "event_type": "exit",
    }
    state["events"].append(out)
    return state


def record_textbox_remove_highlights_fn(
    state: dict[str, Any], textbox_content: dict, lc_state: dict[str, Any]
) -> dict[str, Any]:
    current_text = "".join(
        f"<h>{text}</h>" if tag_id is not None else text for text, tag_id in textbox_content["data"]
    )
    out = {
        "time": get_current_time(),
        "login_code": lc_state["login_code_txt"],
        "text_id": textbox_content["id"],
        "event_type": "remove_highlights",
        "text": current_text,
    }
    state[textbox_content["id"]] = current_text
    state["events"].append(out)
    return state


def record_trial_end_fn(state: dict[str, Any], lc_state: dict[str, Any]) -> dict[str, Any]:
    out = {
        "time": get_current_time(),
        "login_code": lc_state["login_code_txt"],
        "event_type": "end",
    }
    state["events"].append(out)
    return state

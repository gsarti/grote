from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Literal

import gradio as gr
from gradio_highlightedtextbox import HighlightedTextbox

from grote.collections.base import COMPONENT_CONFIGS, ComponentCollection, buildmethod
from grote.config import CONFIG as cfg
from grote.event_logging import HuggingFaceDatasetEventSaver
from grote.functions import record_textbox_blur_fn, record_textbox_focus_fn, record_textbox_input_fn

TRANS_CFG = COMPONENT_CONFIGS["translate"]


@dataclass
class TranslateComponents(ComponentCollection):
    _id: str = "translate"

    reload_btn: gr.Button = None
    done_btn: gr.Button = None
    textboxes_col: gr.Column = None

    @property
    def textboxes(self) -> list[gr.Textbox | HighlightedTextbox]:
        return [c for c in self.components if isinstance(c, (gr.Textbox, HighlightedTextbox))]

    @property
    def target_textboxes(self) -> list[HighlightedTextbox]:
        return [
            c for c in self.components if isinstance(c, HighlightedTextbox) and re.match(r"target_\d+_txt", c.elem_id)
        ]

    @classmethod
    def get_reload_btn(cls, visible: bool = False) -> gr.Button:
        return gr.Button(TRANS_CFG["reload_button_label"], variant="secondary", elem_id="reload_btn", visible=visible)

    @classmethod
    def get_done_btn(cls, visible: bool = False) -> gr.Button:
        return gr.Button(TRANS_CFG["done_button_label"], variant="primary", elem_id="done_btn", visible=visible)

    @classmethod
    def get_textboxes_col(cls, visible: bool = False) -> gr.Column:
        return gr.Column(visible=visible, elem_id="textboxes_col")

    @classmethod
    def get_textbox_txt(
        cls,
        type: Literal["source", "target"],
        id: int,
        value: str | Callable = "",
        visible: bool = False,
        lines: int = 2,
        show_legend: bool = False,
    ) -> gr.components.Textbox | HighlightedTextbox:
        if type == "source":
            return gr.Textbox(
                label=TRANS_CFG["source_textbox_label"],
                lines=lines,
                elem_id=f"{type}_{id}_txt",
                value=value,
                visible=visible,
            )
        elif type == "target":
            return HighlightedTextbox(
                value=HighlightedTextbox.tagged_text_to_tuples(value, TRANS_CFG["highlight_label"]),
                label=TRANS_CFG["target_textbox_label"],
                elem_id=f"{type}_{id}_txt",
                interactive=True,
                show_legend=show_legend,
                combine_adjacent=True,
                visible=visible,
            )

    @classmethod
    @buildmethod
    def build(
        cls: TranslateComponents,
        source_sentences: list[str] = [""] * cfg.max_num_sentences,
        target_sentences: list[str] = [""] * cfg.max_num_sentences,
    ) -> TranslateComponents:
        tc = TranslateComponents()
        with tc.get_textboxes_col(visible=False) as textboxes_col:
            for idx, (src_sent, tgt_sent) in enumerate(zip(source_sentences, target_sentences)):
                with gr.Row(equal_height=True, visible=False):
                    _ = tc.get_textbox_txt("source", idx, src_sent, lines=0)
                    _ = tc.get_textbox_txt("target", idx, tgt_sent, lines=0)
        with gr.Row(equal_height=True):
            tc.reload_btn = tc.get_reload_btn()
            tc.done_btn = tc.get_done_btn()
        tc.textboxes_col = textboxes_col
        return tc

    def set_listeners(self, out_state: gr.State, lc_state: gr.State, writer: HuggingFaceDatasetEventSaver) -> None:
        def save_logs_callback(state: dict[str, Any]) -> dict[str, Any]:
            if len(state["events"]) > cfg.event_logs_save_frequency:
                writer.save(state["events"])
                state["events"] = []
            return state

        def save_logs_callback_no_check(state: dict[str, Any]) -> dict[str, Any]:
            writer.save(state["events"])
            state["events"] = []
            return state

        for textbox in self.target_textboxes:
            textbox.focus(
                record_textbox_focus_fn,
                inputs=[out_state, textbox, lc_state],
                outputs=[out_state],
            )

            textbox.input(
                record_textbox_input_fn,
                inputs=[out_state, textbox, lc_state],
                outputs=[out_state],
                concurrency_limit=50,
                trigger_mode="multiple",
            )

            textbox.blur(
                record_textbox_blur_fn,
                inputs=[out_state, textbox, lc_state],
                outputs=[out_state],
            ).then(
                save_logs_callback_no_check,
                inputs=[out_state],
                outputs=[out_state],
            )

            self.done_btn.click(
                save_logs_callback,
                inputs=[out_state],
                outputs=[out_state],
            ).then(None, js="window.location.reload()")

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Literal

import gradio as gr

from grote.collections.base import COMPONENT_CONFIGS, ComponentCollection, buildmethod
from grote.utils import CONFIG as cfg
from grote.utils import tagged_text_to_tuples

TRANS_CFG = COMPONENT_CONFIGS["translate"]


@dataclass
class TranslateComponents(ComponentCollection):
    _id: str = "translate"

    reload_btn: gr.Button = None
    clear_btn: gr.Button = None
    done_btn: gr.Button = None
    textboxes_col: gr.Column = None

    def get_textboxes(self, count: int = -1):
        return [c for c in self.textboxes_col.children if isinstance(c, gr.components.Component)][:count]

    def get_target_textboxes(self, count: int, target_pattern: str = r"target_\d+_txt"):
        return [
            c
            for c in self.textboxes_col.children
            if isinstance(c, gr.HighlightedTextbox) and re.match(target_pattern, c.elem_id)
        ][:count]

    @classmethod
    def get_reload_btn(cls, visible: bool = False) -> gr.Button:
        return gr.Button(TRANS_CFG["reload_button_label"], variant="secondary", elem_id="reload_btn", visible=visible)

    @classmethod
    def get_clear_btn(cls, visible: bool = False) -> gr.Button:
        return gr.Button(TRANS_CFG["clear_button_label"], variant="secondary", elem_id="clear_btn", visible=visible)

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
    ) -> gr.components.Textbox | gr.components.HighlightedTextbox:
        if type == "source":
            return gr.Textbox(
                label=TRANS_CFG["source_textbox_label"],
                lines=lines,
                elem_id=f"{type}_{id}_txt",
                value=value,
                visible=visible,
            )
        elif type == "target":
            return gr.HighlightedTextbox(
                value=tagged_text_to_tuples(value, tag_id=TRANS_CFG["highlight_label"]),
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
        with gr.Row(equal_height=True):
            tc.reload_btn = tc.get_reload_btn()
            tc.clear_btn = tc.get_clear_btn()
        with tc.get_textboxes_col(visible=False) as textboxes_col:
            for idx, (src_sent, tgt_sent) in enumerate(zip(source_sentences, target_sentences)):
                with gr.Row(equal_height=True, visible=False):
                    _ = tc.get_textbox_txt("source", idx, src_sent, lines=0)
                    _ = tc.get_textbox_txt("target", idx, tgt_sent, lines=0)
        tc.done_btn = tc.get_done_btn()
        tc.textboxes_col = textboxes_col
        return tc

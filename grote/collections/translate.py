from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Literal

import gradio as gr
from gradio_highlightedtextbox import HighlightedTextbox

from grote.collections.base import COMPONENT_CONFIGS, ComponentCollection, buildmethod
from grote.config import CONFIG as cfg
from grote.event_logging import EventLogger
from grote.functions import (
    record_textbox_blur_fn,
    record_textbox_focus_fn,
    record_textbox_input_fn,
    record_textbox_remove_highlights_fn,
    record_trial_end_fn,
    save_outputs_to_file,
)

TRANS_CFG = COMPONENT_CONFIGS["translate"]


@dataclass
class TranslateComponents(ComponentCollection):
    _id: str = "translate"

    source_side_label: gr.Markdown = None
    target_side_label: gr.Markdown = None
    target_side_legend: gr.Markdown = None
    reload_btn: gr.Button = None
    done_btn: gr.Button = None
    download_btn: gr.DownloadButton = None
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
    def get_source_side_label_cap(cls, value: str | None = None, visible: bool = False) -> gr.Markdown:
        if not value:
            value = TRANS_CFG["source_side_label"]
        return gr.Markdown(value, visible=visible, elem_id="source_side_label_cap")

    @classmethod
    def get_target_side_label_cap(cls, value: str | None = None, visible: bool = False) -> gr.Markdown:
        if not value:
            value = TRANS_CFG["target_side_label"]
        return gr.Markdown(value, visible=visible, elem_id="target_side_label_cap")

    @classmethod
    def get_target_side_legend_cap(cls, value: str | None = None, visible: bool = False) -> gr.Markdown:
        if not value and cfg.tag_labels and cfg.tag_colors:
            value = f"<b>{TRANS_CFG['legend_label']}:</b>" + "".join(
                f'<span style="background-color:{color}; margin-left: 0.5em; color: black; padding: 0px 5px;">{label}</span>'
                for label, color in zip(cfg.tag_labels, cfg.tag_colors)
            )
        return gr.Markdown(value, visible=visible, elem_id="target_side_legend_cap")

    @classmethod
    def get_reload_btn(cls, visible: bool = False) -> gr.Button:
        return gr.Button(TRANS_CFG["reload_button_label"], variant="secondary", elem_id="reload_btn", visible=visible)

    @classmethod
    def get_done_btn(cls, visible: bool = False) -> gr.Button:
        return gr.Button(TRANS_CFG["done_button_label"], variant="primary", elem_id="done_btn", visible=visible)

    @classmethod
    def get_download_btn(cls, visible: bool = False) -> gr.DownloadButton:
        return gr.DownloadButton(
            TRANS_CFG["download_button_label"],
            variant="primary",
            elem_id="download_btn",
            visible=visible,
            interactive=False,
        )

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
    ) -> gr.components.Textbox | HighlightedTextbox:
        if type == "source":
            return gr.Textbox(
                label=TRANS_CFG["source_textbox_label"],
                lines=lines,
                elem_id=f"{type}_{id}_txt",
                value=value,
                visible=visible,
                elem_classes=["source-textbox"],
                show_label=False,
            )
        elif type == "target":
            tuples = HighlightedTextbox.tagged_text_to_tuples(
                value,
                tag_ids=cfg.tag_labels,
                tags_open=[f"<{tag}>" for tag in cfg.allowed_tags],
                tags_close=[f"</{tag}>" for tag in cfg.allowed_tags],
            )
            color_map = None
            if cfg.tag_colors:
                if len(cfg.tag_colors) != len(cfg.tag_labels):
                    raise ValueError("highlight_colors and highlight_labels must have the same length")
                color_map = dict(zip(cfg.tag_labels, cfg.tag_colors))
            return HighlightedTextbox(
                value=tuples,
                label=TRANS_CFG["target_textbox_label"],
                elem_id=f"{type}_{id}_txt",
                interactive=True,
                show_label=False,
                show_legend=False,
                combine_adjacent=True,
                visible=visible,
                show_remove_tags_button=True,
                color_map=color_map,
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
            tc.source_side_label = tc.get_source_side_label_cap()
            with gr.Column(visible=True):
                tc.target_side_label = tc.get_target_side_label_cap()
                tc.target_side_legend = tc.get_target_side_legend_cap()
        with tc.get_textboxes_col(visible=False) as textboxes_col:
            for idx, (src_sent, tgt_sent) in enumerate(zip(source_sentences, target_sentences)):
                with gr.Row(equal_height=True, visible=False):
                    _ = tc.get_textbox_txt("source", idx, src_sent, lines=0)
                    _ = tc.get_textbox_txt("target", idx, tgt_sent, lines=0)
        with gr.Row(equal_height=True):
            tc.reload_btn = tc.get_reload_btn()
            tc.done_btn = tc.get_done_btn()
        tc.download_btn = tc.get_download_btn()
        tc.textboxes_col = textboxes_col
        return tc

    def set_listeners(self, out_state: gr.State, lc_state: gr.State, logger: EventLogger) -> None:
        def save_logs_callback(state: dict[str, Any]) -> dict[str, Any]:
            if len(state["events"]) > cfg.event_logs_save_frequency:
                logger.save(state["events"])
                state["events"] = []
            return state

        def save_logs_callback_no_check(state: dict[str, Any]) -> dict[str, Any]:
            logger.save(state["events"])
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
                save_logs_callback,
                inputs=[out_state],
                outputs=[out_state],
            )

            textbox.clear(
                record_textbox_remove_highlights_fn,
                inputs=[out_state, textbox, lc_state],
                outputs=[out_state],
                trigger_mode="multiple",
            ).then(
                save_logs_callback,
                inputs=[out_state],
                outputs=[out_state],
            )

        self.done_btn.click(
            record_trial_end_fn,
            inputs=[out_state, lc_state],
            outputs=[out_state],
        ).then(
            save_logs_callback_no_check,
            inputs=[out_state],
            outputs=[out_state],
        ).then(
            save_outputs_to_file,
            inputs=[lc_state] + self.target_textboxes,
            outputs=[self.download_btn, self.done_btn],
        )

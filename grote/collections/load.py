from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import gradio as gr

from grote.collections.base import COMPONENT_CONFIGS, ComponentCollection, buildmethod
from grote.collections.translate import TranslateComponents
from grote.functions import check_inputs_fn, initialize_translate_fn, parse_inputs_fn, set_start_time_fn

LOAD_CFG = COMPONENT_CONFIGS["load"]


@dataclass
class LoadComponents(ComponentCollection):
    _id: str = "load"

    login_code_description_cap: gr.Markdown = None
    login_code_txt: gr.Textbox = None
    source_input_description_cap: gr.Markdown = None
    source_file_in: gr.File = None
    source_sentences_txt: gr.Textbox = None
    target_input_description_cap: gr.Markdown = None
    target_file_in: gr.File = None
    target_sentences_txt: gr.Textbox = None
    start_btn: gr.Button = None

    @classmethod
    def get_login_code_description_cap(cls, value: str | None = None, visible: bool = True) -> gr.Markdown:
        if not value:
            value = LOAD_CFG["login_code_description"]
        return gr.Markdown(value, visible=visible, elem_id="login_code_description_cap")

    @classmethod
    def get_login_code_txt(cls, value: str | Callable = "", visible: bool = True) -> gr.components.Textbox:
        return gr.Textbox(
            label=LOAD_CFG["login_code_label"],
            lines=1,
            elem_id="login_code_txt",
            placeholder=LOAD_CFG["login_code_placeholder"],
            value=value,
            visible=visible,
            info=LOAD_CFG["login_code_info"],
        )

    @classmethod
    def get_source_input_description_cap(cls, value: str | None = None, visible: bool = True) -> gr.Markdown:
        if not value:
            value = LOAD_CFG["source_input_description"]
        return gr.Markdown(value, visible=visible, elem_id="source_input_description_cap")

    @classmethod
    def get_source_file_in(cls, value: str | list[str] | Callable | None = None, visible: bool = True) -> gr.File:
        return gr.File(
            label=LOAD_CFG["source_file_label"],
            interactive=True,
            elem_id="source_file_in",
            height=200,
            file_count="single",
            file_types=["txt"],
            value=value,
            visible=visible,
        )

    @classmethod
    def get_source_sentences_txt(cls, value: str | Callable = "", visible: bool = True) -> gr.components.Textbox:
        return gr.Textbox(
            label=LOAD_CFG["source_sentences_label"],
            lines=6,
            elem_id="source_sentences_txt",
            placeholder=LOAD_CFG["source_sentences_placeholder"],
            value=value,
            visible=visible,
        )

    @classmethod
    def get_target_input_description_cap(cls, value: str | None = None, visible: bool = True) -> gr.Markdown:
        if not value:
            value = LOAD_CFG["target_input_description"]
        return gr.Markdown(value, visible=visible, elem_id="target_input_description_cap")

    @classmethod
    def get_target_file_in(cls, value: str | list[str] | Callable | None = None, visible: bool = True) -> gr.File:
        return gr.File(
            label=LOAD_CFG["target_file_label"],
            interactive=True,
            elem_id="target_file_in",
            height=200,
            file_count="single",
            file_types=["txt"],
            value=value,
            visible=visible,
        )

    @classmethod
    def get_target_sentences_txt(cls, value: str | Callable = "", visible: bool = True) -> gr.Textbox:
        return gr.Textbox(
            label=LOAD_CFG["target_sentences_label"],
            lines=6,
            elem_id="target_sentences_txt",
            placeholder=LOAD_CFG["target_sentences_placeholder"],
            value=value,
            visible=visible,
        )

    @classmethod
    def get_start_btn(cls, visible: bool = True) -> gr.Button:
        return gr.Button(LOAD_CFG["start_button_label"], variant="primary", elem_id="start_btn", visible=visible)

    @classmethod
    @buildmethod
    def build(cls: LoadComponents) -> LoadComponents:
        lc: LoadComponents = cls()
        lc.login_code_description_cap = lc.get_login_code_description_cap()
        lc.login_code_txt = lc.get_login_code_txt()
        lc.source_input_description_cap = lc.get_source_input_description_cap()
        with gr.Row(equal_height=True):
            lc.source_file_in = lc.get_source_file_in()
            lc.source_sentences_txt = lc.get_source_sentences_txt()
        lc.target_input_description_cap = lc.get_target_input_description_cap()
        with gr.Row(equal_height=True):
            lc.target_file_in = lc.get_target_file_in()
            lc.target_sentences_txt = lc.get_target_sentences_txt()
        lc.start_btn = lc.get_start_btn()
        return lc

    def set_loading_listeners(self, tc: TranslateComponents, out_state: gr.State) -> None:
        self.start_btn.click(
            check_inputs_fn,
            inputs=[
                self.login_code_txt,
                self.source_file_in,
                self.target_file_in,
                self.source_sentences_txt,
                self.target_sentences_txt,
            ],
            outputs=[],
        ).success(
            parse_inputs_fn,
            inputs=[
                self.login_code_txt,
                self.source_file_in,
                self.target_file_in,
                self.source_sentences_txt,
                self.target_sentences_txt,
                self.state,
            ],
            outputs=[
                self.login_code_txt,
                self.source_file_in,
                self.target_file_in,
                self.source_sentences_txt,
                self.target_sentences_txt,
                self.state,
            ],
        ).success(
            initialize_translate_fn,
            inputs=[self.state, tc.state],
            outputs=[tc.textboxes_col]
            + self.components
            + tc.components
            + [c for c in tc.textboxes_col.children if isinstance(c, gr.Row)],
        ).success(
            set_start_time_fn,
            inputs=[out_state],
            outputs=[out_state],
        )

    def clear_changes_listener(self, tc: TranslateComponents, out_state: gr.State) -> None:
        tc.clear_btn.click(
            initialize_translate_fn,
            inputs=[self.state, tc.state],
            outputs=[tc.textboxes_col]
            + self.components
            + tc.components
            + [c for c in tc.textboxes_col.children if isinstance(c, gr.Row)],
        ).success(
            set_start_time_fn,
            inputs=[out_state],
            outputs=[out_state],
        )

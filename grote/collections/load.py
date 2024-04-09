from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import gradio as gr

from grote.collections.base import COMPONENT_CONFIGS, ComponentCollection, buildmethod
from grote.collections.translate import TranslateComponents
from grote.functions import check_and_parse_inputs_fn, initialize_translate_interface_fn, record_trial_start_fn

LOAD_CFG = COMPONENT_CONFIGS["load"]


@dataclass
class LoadComponents(ComponentCollection):
    _id: str = "load"

    login_code_description_cap: gr.Markdown = None
    login_code_txt: gr.Textbox = None
    input_description_cap: gr.Markdown = None
    file_in: gr.File = None
    sentences_txt: gr.Textbox = None
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
    def get_input_description_cap(cls, value: str | None = None, visible: bool = True) -> gr.Markdown:
        if not value:
            value = LOAD_CFG["input_description"]
        return gr.Markdown(value, visible=visible, elem_id="input_description_cap")

    @classmethod
    def get_file_in(cls, value: str | list[str] | Callable | None = None, visible: bool = True) -> gr.File:
        return gr.File(
            label=LOAD_CFG["file_label"],
            interactive=True,
            elem_id="file_in",
            file_count="single",
            file_types=["txt"],
            value=value,
            visible=visible,
        )

    @classmethod
    def get_sentences_txt(cls, value: str | Callable = "", visible: bool = False) -> gr.components.Textbox:
        return gr.Textbox(
            label=LOAD_CFG["sentences_label"],
            lines=6,
            elem_id="sentences_txt",
            placeholder=LOAD_CFG["sentences_placeholder"],
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
        lc.input_description_cap = lc.get_input_description_cap()
        lc.file_in = lc.get_file_in()
        lc.sentences_txt = lc.get_sentences_txt()
        lc.start_btn = lc.get_start_btn()
        return lc

    def set_listeners(self, tc: TranslateComponents, out_state: gr.State) -> None:
        self.start_btn.click(
            check_and_parse_inputs_fn,
            inputs=[
                self.login_code_txt,
                self.file_in,
                self.sentences_txt,
                self.state,
            ],
            outputs=[
                self.state,
            ],
        ).success(
            initialize_translate_interface_fn,
            inputs=[self.state, tc.state],
            outputs=[tc.textboxes_col]
            + self.components
            + tc.components
            + [c for c in tc.textboxes_col.children if isinstance(c, gr.Row)],
        ).success(
            record_trial_start_fn,
            inputs=[out_state, self.state],
            outputs=[out_state],
        )

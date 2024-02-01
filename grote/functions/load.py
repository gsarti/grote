import re
from typing import Any

import gradio as gr

from grote.config import CONFIG as cfg


def check_inputs_fn(
    login_code_txt: str,
    source_file_in: gr.File,
    target_file_in: gr.File,
    source_sentences_txt: str,
    target_sentences_txt: str,
) -> None:
    """Checks if the loading inputs are valid.

    Args:
        login_code_txt (`str`):
            Textbox containing the login code.
        source_file_in (`gr.File`):
            File containing source sentences to be translated.
        target_file_in (`gr.File`):
            File containing pretranslated sentences.
        source_sentences_txt (`str`):
            Textbox containing source sentences to be translated. Specified as an alternative to `source_file_in`.
        target_sentences_txt (`str`):
            Textbox containing pretranslated sentences. Specified as an alternative to `target_file_in`.

    Raises:
        `gr.Error`: Invalid login code.
        `gr.Error`: No source sentences were provided in either `source_file_in` or `source_sentences_txt`.
        `gr.Error`: Source sentences were provided in both `source_file_in` and `source_sentences_txt`.
        `gr.Error`: No target sentences were provided in either `target_file_in` or `target_sentences_txt`.
        `gr.Error`: Target sentences were provided in both `target_file_in` and `target_sentences_txt`.
        `gr.Error`: The number of source and target sentences does not match.
        `gr.Error`: Source sentences cannot contain highlights.
        `gr.Error`: Target sentences cannot contain unclosed highlights.
        `gr.Error`: Target sentences cannot contain invalid highlights (wrong order or wrong type)
    """
    if login_code_txt not in cfg.login_codes:
        raise gr.Error("ERROR: Invalid login code.")
    if not source_file_in and not source_sentences_txt:
        raise gr.Error("ERROR: No source sentences were provided.")
    elif source_file_in and source_sentences_txt:
        raise gr.Error("ERROR: You can either upload a file or insert sentences manually, not both.")

    if not target_file_in and not target_sentences_txt:
        raise gr.Error("ERROR: No target sentences were provided.")
    elif target_file_in and target_sentences_txt:
        raise gr.Error("ERROR: You can either upload a file or insert sentences manually, not both.")

    if len(source_sentences_txt.split("\n")) != len(target_sentences_txt.split("\n")):
        raise gr.Error("ERROR: The number of source and target sentences must be equal.")

    # Check wellformedness of source and target sentences (highlights allowed in target sentences only)
    find_tag_pattern = r"(<\/?h>)"
    source_matches = [(m.group(0),) + m.span() for m in re.finditer(find_tag_pattern, source_sentences_txt)]
    if len(source_matches) > 0:
        raise gr.Error("ERROR: Source sentences cannot contain highlights.")
    for tgt_sent_idx, target_sentence in enumerate(target_sentences_txt.split("\n"), start=1):
        target_matches = [(m.group(0),) + m.span() for m in re.finditer(find_tag_pattern, target_sentence)]
        num_matches = len(target_matches)
        if num_matches > 0:
            if num_matches % 2 != 0:
                raise gr.Error(f"ERROR: Target sentence {tgt_sent_idx} contains an unclosed highlight.")
            for curr_match_idx, match in enumerate(target_matches, start=1):
                if (curr_match_idx % 2 != 0 and match[0] != "<h>") or (curr_match_idx % 2 == 0 and match[0] != "</h>"):
                    raise gr.Error(
                        f"ERROR: Target sentence {tgt_sent_idx} contains an invalid highlight ({curr_match_idx},"
                        f" {match[0]})."
                    )
    gr.Info("Inputs validated successfully!")


def parse_inputs_fn(
    login_code_txt: str,
    src_file_in: gr.File,
    tgt_file_in: gr.File,
    src_sentences_txt: str,
    tgt_sentences_txt: str,
    state: dict[str, Any],
) -> list[str]:
    from grote.collections import LoadComponents

    if src_file_in is not None:
        with open(src_file_in.name) as f:
            src_sentences_txt = ("".join(f.readlines())).strip(" ").strip("\n")
        state["source_file_in"] = None
    if tgt_file_in is not None:
        with open(tgt_file_in.name) as f:
            tgt_sentences_txt = ("".join(f.readlines())).strip(" ").strip("\n")
        state["target_file_in"] = None
    empty_src_file = LoadComponents.get_source_file_in(value=None)
    empty_tgt_file = LoadComponents.get_target_file_in(value=None)
    state["login_code_txt"] = login_code_txt
    state["source_file_in"] = None
    state["target_file_in"] = None
    state["source_sentences_txt"] = src_sentences_txt
    state["target_sentences_txt"] = tgt_sentences_txt
    return login_code_txt, empty_src_file, empty_tgt_file, src_sentences_txt, tgt_sentences_txt, state


def initialize_translate_fn(lc_state: dict[str, Any], tc_state: dict[str, Any]):
    """Initializes the translation tab."""
    from grote.collections import LoadComponents, TranslateComponents

    source_sentences = lc_state["source_sentences_txt"].split("\n")
    target_sentences = lc_state["target_sentences_txt"].split("\n")
    num_sentences = len(source_sentences)
    lc_components = []
    for lc_elem_id in lc_state.keys():
        if not lc_elem_id.startswith("_"):
            lc_components.append(LoadComponents.make_component(lc_elem_id, visible=False))
    tc_components = []
    for tc_elem_id in tc_state.keys():
        if not tc_elem_id.startswith("_") and not tc_elem_id.endswith("_txt"):
            tc_components.append(TranslateComponents.make_component(tc_elem_id, visible=True))
    for tc_elem_id in [k for k in tc_state.keys() if k.endswith("_txt")]:
        txt_type, txt_id, _ = tc_elem_id.split("_")
        if int(txt_id) < len(source_sentences):
            if txt_type == "source":
                curr_sent = source_sentences[int(txt_id)]
            elif txt_type == "target":
                curr_sent = target_sentences[int(txt_id)]
            tc_components.append(
                TranslateComponents.get_textbox_txt(
                    txt_type, txt_id, curr_sent, visible=True, show_legend=int(txt_id) == 0
                )
            )
            tc_state[f"{txt_type}_{txt_id}_txt"] = curr_sent
        else:
            tc_components.append(TranslateComponents.get_textbox_txt(txt_type, txt_id, "", visible=False))
    n_hid = cfg.max_num_sentences - num_sentences
    return (
        [TranslateComponents.get_textboxes_col(visible=True)]
        + [lc_state]
        + lc_components
        + [tc_state]
        + tc_components
        + [gr.Row(visible=True) for _ in range(num_sentences)]
        + [gr.Row(visible=False) for _ in range(n_hid)]
    )

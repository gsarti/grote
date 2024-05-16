import re
from pathlib import Path
from typing import Any

import gradio as gr

from grote.config import CONFIG as cfg


def check_and_parse_inputs_fn(
    login_code_txt: str,
    file_in: gr.File,
    sentences_txt: str,
    state: dict[str, Any],
) -> None:
    """Checks if the loading inputs are valid.

    Args:
        login_code_txt (`str`):
            Textbox containing the login code.
        file_in (`gr.File`):
            File containing source and target sentences in `SRC ||| TGT` format.
        sentences_txt (`str`):
            Textbox containing source and target sentences in `SRC ||| TGT` format. Can be used instead of `file_in`.
        state (`dict`):
            The current state of the load tab in the application.

    Raises:
        `gr.Error`: Invalid login code.
        `gr.Error`: No sentences were provided in either `source_file_in` or `source_sentences_txt`.
        `gr.Error`: Sentences were provided in both `source_file_in` and `source_sentences_txt`.
        `gr.Error`: Sentences must match the format SOURCE ||| TARGET.
        `gr.Error`: Source sentences cannot contain highlights.
        `gr.Error`: Target sentences cannot contain unclosed highlights.
        `gr.Error`: Target sentences cannot contain invalid highlights (wrong order or wrong type)
    """
    if login_code_txt not in cfg.login_codes:
        raise gr.Error("ERROR: Invalid login code.")
    if not file_in and not sentences_txt:
        raise gr.Error("ERROR: No sentences were provided.")
    elif file_in and sentences_txt:
        raise gr.Error("ERROR: You can either upload a file or insert sentences manually, not both.")

    if file_in is not None:
        with open(file_in.name) as f:
            sentences_txt = f.read()
            # remove empty lines
            sentences_txt = re.sub(r"\n+", "\n", sentences_txt)
    sentences_txt = sentences_txt.strip().split("\n")

    if not all(" ||| " in s for s in sentences_txt):
        raise gr.Error("ERROR: Sentences must match the format SOURCE ||| TARGET")

    source_sentences = [sent.split(" ||| ")[0] for sent in sentences_txt]
    target_sentences = [sent.split(" ||| ")[1] for sent in sentences_txt]
    # Check wellformedness of source and target sentences (highlights allowed in target sentences only)
    find_tag_pattern = rf"(<\/?(?:{'|'.join(cfg.allowed_tags)})>)"
    open_tags = [f"<{tag}>" for tag in cfg.allowed_tags]
    close_tags = [f"</{tag}>" for tag in cfg.allowed_tags]
    source_matches = [(m.group(0),) + m.span() for m in re.finditer(find_tag_pattern, "\n".join(source_sentences))]
    if len(source_matches) > 0:
        raise gr.Error("ERROR: Source sentences cannot contain highlights.")
    state["_has_highlights"] = False
    for tgt_sent_idx, target_sentence in enumerate(target_sentences, start=1):
        target_matches = [(m.group(0),) + m.span() for m in re.finditer(find_tag_pattern, target_sentence)]
        num_matches = len(target_matches)
        if num_matches > 0:
            if num_matches % 2 != 0:
                raise gr.Error(f"ERROR: Target sentence {tgt_sent_idx} contains an unclosed highlight.")
            for curr_match_idx, match in enumerate(target_matches, start=1):
                if (curr_match_idx % 2 != 0 and match[0] not in open_tags) or (
                    curr_match_idx % 2 == 0 and match[0] not in close_tags
                ):
                    raise gr.Error(
                        f"ERROR: Target sentence {tgt_sent_idx} contains an invalid highlight ({curr_match_idx},"
                        f" {match[0]})."
                    )
            state["_has_highlights"] = True
    state["login_code_txt"] = login_code_txt
    state["file_in"] = None
    state["_filename"] = Path(file_in.name).stem if file_in is not None else "grote_sentences.txt"
    state["sentences_txt"] = sentences_txt
    return state


def initialize_translate_interface_fn(lc_state: dict[str, Any], tc_state: dict[str, Any]):
    """Initializes the translation tab."""
    from grote.collections import LoadComponents, TranslateComponents

    sentences = lc_state["sentences_txt"]
    source_sentences = [sent.split(" ||| ")[0].strip() for sent in sentences]
    target_sentences = [sent.split(" ||| ")[1].strip() for sent in sentences]
    num_sentences = len(sentences)
    lc_components = []
    for lc_elem_id in lc_state.keys():
        if not lc_elem_id.startswith("_"):
            lc_components.append(LoadComponents.make_component(lc_elem_id, visible=False))
    tc_components = []
    for tc_elem_id in tc_state.keys():
        if not tc_elem_id.startswith("_") and not tc_elem_id.endswith("_txt"):
            tc_components.append(
                TranslateComponents.make_component(
                    tc_elem_id, visible=True, has_highlights=lc_state["_has_highlights"]
                )
            )
    for tc_elem_id in [k for k in tc_state.keys() if k.endswith("_txt")]:
        txt_type, txt_id, _ = tc_elem_id.split("_")
        if int(txt_id) < len(source_sentences):
            if txt_type == "source":
                curr_sent = source_sentences[int(txt_id)]
            elif txt_type == "target":
                curr_sent = target_sentences[int(txt_id)]
            tc_components.append(
                TranslateComponents.get_textbox_txt(
                    txt_type, txt_id, curr_sent, visible=True, has_highlights=lc_state["_has_highlights"]
                )
            )
            tc_state[f"{txt_type}_{txt_id}_txt"] = curr_sent
        else:
            tc_components.append(
                TranslateComponents.get_textbox_txt(
                    txt_type, txt_id, "", visible=False, has_highlights=lc_state["_has_highlights"]
                )
            )
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

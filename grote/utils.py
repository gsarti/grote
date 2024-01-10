from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class GroteConfig:
    max_num_sentences: int
    login_codes: list[str]
    translate_tab_label: str


CONFIG = GroteConfig(**yaml.safe_load(open(Path(__file__).parent / "config.yaml", encoding="utf8")))


def tagged_text_to_tuples(
    text: str, tag_id: str, tag_open: str = "<h>", tag_close: str = "</h>"
) -> list[tuple[str, str | None]]:
    """Parse a text containing tags into a list of tuples in the format accepted by HighlightedTextbox.

    E.g. Hello <h>world</h>! -> [("Hello", None), ("world", <TAG_ID>), ("!", None)]

    Args:
        text (`str`):
            Text containing tags that needs to be parsed.
        tag_id (`str`):
            Label to use for the second element of the tuple.
        tag_open (`str`, *optional*, defaults to "<h>"):
            Tag used to mark the beginning of a highlighted section.
        tag_close (`str`, *optional*, defaults to "</h>"):
            Tag used to mark the end of a highlighted section.

    Raises:
        `ValueError`: Number of open tags does not match number of closed tags.

    Returns:
        `list[tuple[str, str | None]]`: List of tuples in the format accepted by HighlightedTextbox.
    """
    # Check that the text is well-formed (i.e. no nested or empty tags)
    num_tags = text.count(tag_open)
    if num_tags != text.count(tag_close):
        raise ValueError(f"Number of open tags ({tag_open}) does not match number of closed tags ({tag_close}).")
    elif num_tags == 0:
        return [(text, None)]
    elif num_tags > 0:
        out = []
        pre_tag_text = text[: text.index(tag_open)]
        if pre_tag_text:
            out += [(pre_tag_text.strip(), None)]

        tag_text = text[text.index(tag_open) + len(tag_open) : text.index(tag_close)]
        out += [(tag_text.strip(), tag_id)]
        if num_tags > 1:
            remaining_text = text[text.index(tag_close) + len(tag_close) :]
            out += tagged_text_to_tuples(remaining_text, tag_id=tag_id, tag_open=tag_open, tag_close=tag_close)
        else:
            post_tag_text = text[text.index(tag_close) + len(tag_close) :]
            if post_tag_text:
                out += [(post_tag_text, None)]
    return out

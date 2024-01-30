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

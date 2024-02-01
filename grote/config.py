from __future__ import annotations

import os
from dataclasses import dataclass, fields
from pathlib import Path

import yaml


@dataclass
class GroteConfig:
    max_num_sentences: int
    login_codes: list[str]
    translate_tab_label: str
    grote_logo_path: str
    grote_icon_path: str
    event_logs_save_frequency: int
    event_logs_hf_dataset_id: str
    event_logs_local_dir: str
    hf_token: str | None = None


CONFIG = GroteConfig(
    **yaml.safe_load(open(Path(__file__).parent / "config.yaml", encoding="utf8")),
    **{k.lower(): v for k, v in os.environ.items() if k.lower() in [f.name.lower() for f in fields(GroteConfig)]},
)

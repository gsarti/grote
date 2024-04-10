from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from pathlib import Path

import yaml


@dataclass
class GroteConfig:
    """Main configuration for the Grote application.

    Attributes:

    max_num_sentences: int
        The maximum number of sentences to be displayed at once in the translation tab. This is necessary
        since textboxes cannot be created dynamically in Gradio.
    login_codes: list[str]
        The list of valid login codes for the application.
    event_logs_save_frequency: int
        The frequency at which to save event logs expressed in number of events. Any change in the input of the
        textboxes will be logged as an event (e.g. one event per keystroke), and special events are stored for
        focus, blur, and removal of highlights.
    event_logs_hf_dataset_id: str
        The Hugging Face dataset ID to save the event logs to.
    event_logs_local_dir: str
        The local directory where the event logs are saved.
    hf_token: str | None
        The Hugging Face token to use to create (and write the logged sample to) the Hugging Face dataset
        (defaults to the registered one).
    allowed_tags: list[str]
        The list of allowed tags to be used in the translation tab.
    """

    max_num_sentences: int = 100
    login_codes: str | list[str] = "admin"
    event_logs_save_frequency: int = 50
    event_logs_hf_dataset_id: str = "grote-logs"
    event_logs_local_dir: str = "logs"
    hf_token: str | None = None
    allowed_tags: str | list[str] = field(default_factory=["minor", "major"])
    tag_labels: str | list[str] = field(default_factory=["Minor", "Major"])
    tag_colors: str | list[str] = field(default_factory=["#ffedd5", "#fcd29a"])

    @staticmethod
    def init_list(val: str | list) -> list:
        if isinstance(val, str):
            return val.split(",")
        return val

    @staticmethod
    def parse_int(val: str | int) -> int:
        if isinstance(val, str):
            return int(val)
        return val

    def __post_init__(self):
        self.max_num_sentences = self.parse_int(self.max_num_sentences)
        self.event_logs_save_frequency = self.parse_int(self.event_logs_save_frequency)
        self.login_codes = self.init_list(self.login_codes)
        self.allowed_tags = self.init_list(self.allowed_tags)
        self.tag_labels = self.init_list(self.tag_labels)
        self.tag_colors = self.init_list(self.tag_colors)


# Priority: environment variables > config.yaml
CONFIG = GroteConfig(
    **{
        **yaml.safe_load(open(Path(__file__).parent / "config.yaml", encoding="utf8")),
        **{k.lower(): v for k, v in os.environ.items() if k.lower() in [f.name.lower() for f in fields(GroteConfig)]},
    }
)

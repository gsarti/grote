from __future__ import annotations

from pathlib import Path

import toml


def get_version() -> str | None:
    pyproject_toml_file = Path(__file__).parent.parent / "pyproject.toml"
    if pyproject_toml_file.exists() and pyproject_toml_file.is_file():
        return toml.load(pyproject_toml_file)["tool"]["poetry"]["version"]
    return None


__version__ = get_version()

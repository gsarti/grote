from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Callable, ClassVar, TypeVar

import gradio as gr
import yaml
from gradio.blocks import BlockContext

T = TypeVar("T", bound="ComponentCollection")

NON_EDITABLE_COMPONENTS = [gr.Markdown, gr.Button]

COMPONENT_CONFIGS = yaml.safe_load(open(Path(__file__).parent / "config.yaml", encoding="utf8"))


def buildmethod(f: Callable[..., T]) -> Callable[..., T]:
    @wraps(f)
    def post_build_wrapper(cls, *args, **kwargs):
        component = f(cls, *args, **kwargs)
        component.post_build()
        return component

    return post_build_wrapper


@dataclass
class ComponentCollection:
    """A collection of Gradio components facilitating the creation of Gradio interfaces."""

    _state: gr.State = None
    _id: ClassVar[str] = "base"

    def __post_init__(self):
        pass

    def post_build(self):
        self._state = gr.State({c.elem_id: c.value for c in self.components})

    @classmethod
    def _get_components(cls, item) -> list[gr.components.IOComponent]:
        """Recursive method to extract all IOComponents from a given object"""
        if isinstance(item, gr.components.IOComponent):
            return [item]
        elif isinstance(item, ComponentCollection):
            return item.list_components()
        elif isinstance(item, BlockContext):
            return [subc for c in item.children for subc in cls._get_components(c)]
        elif isinstance(item, list):
            return [subc for c in item for subc in cls._get_components(c)]
        elif isinstance(item, dict):
            return [subc for c in item for subc in cls._get_components(c)]
        else:
            return []

    @property
    def components(self) -> list[gr.components.IOComponent]:
        all_components = []
        for f in self.__dataclass_fields__:
            component = getattr(self, f)
            all_components.extend(ComponentCollection._get_components(component))
        return all_components

    @property
    def editable_components(self) -> list[gr.components.IOComponent]:
        return [c for c in self.components if not isinstance(c, NON_EDITABLE_COMPONENTS)]

    @property
    def state(self) -> gr.State:
        return self._state

    @state.setter
    def state(self, state: gr.State) -> None:
        self._state = state

    @classmethod
    def make_component(cls, elem_id: str, **kwargs) -> gr.components.IOComponent:
        if not hasattr(cls, f"get_{elem_id}"):
            raise ValueError(f"Method get_{elem_id} not found for class {cls.__name__}.")
        return getattr(cls, f"get_{elem_id}")(**kwargs)

    @classmethod
    @buildmethod
    def build(cls: T, **kwargs) -> T:
        raise NotImplementedError

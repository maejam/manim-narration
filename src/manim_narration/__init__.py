import typing as t

import manim

from manim_narration.narration_scene import NarrationScene as NarrationScene

if t.TYPE_CHECKING:
    from manim_narration._config.config import NarrationConfig

__all__ = ["config", "NarrationScene"]


config: "NarrationConfig"


def __getattr__(name: str) -> t.Any:
    """Lazy load the global config object to avoid side-effects."""
    global config
    if name == "config" and "config" not in globals():
        from manim_narration._config.config import NarrationConfig

        config = NarrationConfig(placeholders=manim.config._d)
        return config
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

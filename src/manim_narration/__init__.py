import typing as t

import manim

if t.TYPE_CHECKING:
    from manim_narration.config.config import NarrationConfig

__all__ = ["config"]


config: "NarrationConfig"


def __getattr__(name: str) -> t.Any:
    """Lazy load the global config object."""
    global config
    if name == "config" and "config" not in globals():
        from manim_narration.config.config import NarrationConfig

        config = NarrationConfig(placeholders=manim.config._d)
        return config
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

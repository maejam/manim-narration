import typing as t

from .interpolator import InterpolationAligner
from .manual import ManualAligner

if t.TYPE_CHECKING:
    from .ctc import CTCAligner


__all__ = ["CTCAligner", "InterpolationAligner", "ManualAligner"]


def __getattr__(name: str) -> t.Any:
    """Lazy-load heavy services.

    Improves import times and allow for not installing related groups.

    """
    if name == "CTCAligner":
        from .ctc import CTCAligner

        return CTCAligner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

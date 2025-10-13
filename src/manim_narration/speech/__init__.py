import typing as t

if t.TYPE_CHECKING:
    from .coqui import CoquiService
    from .gtts import GTTSService
    from .kokoro import KokoroService


__all__ = ["CoquiService", "GTTSService", "KokoroService"]


def __getattr__(name: str) -> t.Any:
    """Lazy-load services to improve import times."""
    if name == "CoquiService":
        from .coqui import CoquiService

        return CoquiService
    if name == "GTTSService":
        from .gtts import GTTSService

        return GTTSService
    if name == "KokoroService":
        from .kokoro import KokoroService

        return KokoroService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

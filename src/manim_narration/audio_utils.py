from pathlib import Path

import sox  # type: ignore[import-untyped]

from manim_narration.utils import NarrationError


class NarrationAudioError(NarrationError):
    """Errors related to audio processing."""

    pass


def get_duration(path: Path | str) -> float:
    """Get the duration of an audio file.

    Parameters
    ----------
    path
        The path to the audio file.

    Returns
    -------
    Duration of the audio file in seconds.

    Raises
    ------
    NarrationAudioError
        if sox encounters a problem or returns `None`.
    """
    try:
        duration: float | None = sox.file_info.duration(path)
    except sox.core.SoxiError as e:
        raise NarrationAudioError(
            f"There is a problem with the audio file: `{path}`"
        ) from e
    if duration is None:
        raise NarrationAudioError(
            f"Unable to get the duration of the audio file: `{path}`."
        )
    return duration

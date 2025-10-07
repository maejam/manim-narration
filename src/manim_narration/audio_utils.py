from pathlib import Path

import librosa

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

    """
    duration = librosa.get_duration(path=path)
    return duration

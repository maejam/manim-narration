from functools import lru_cache
from pathlib import Path

import librosa
import soundfile as sf

from manim_narration.utils import NarrationError


class NarrationAudioError(NarrationError):
    """Errors related to audio processing."""

    pass


@lru_cache(maxsize=1)
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


def convert_to_wav(file_path: Path | str, rm_original: bool = True) -> Path:
    """Convert an audio file to .wav format.

    Parameters
    ----------
    file_path
        The path to the audio file to convert.
    rm_original
        Whether to remove the original file once the conversion is done.

    Returns
    -------
    The path to the converted file.

    """
    path = Path(file_path)
    if not path.is_file():
        raise NarrationAudioError(f"`{str(path)}` does not exist or is not a file.")
    if path.suffix == ".wav":
        return path
    # load file, keep original sampling rate and channels
    audio, sr = librosa.load(path, sr=None, mono=False)
    output_path = path.parent / path.stem
    wav_file = output_path.with_suffix(".wav")
    sf.write(wav_file, audio.T, sr, subtype="PCM_16")
    if rm_original:
        path.unlink()
    return wav_file

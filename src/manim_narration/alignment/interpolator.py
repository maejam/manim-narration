from pathlib import Path

from manim_narration import audio_utils as audio

from .aligner_base import AlignmentService


class InterpolationAligner(AlignmentService):
    """A very basic implementation to map character offsets to timestamps.

    Returns
    -------
    A tuple containing the interpolated timestamps.

    """

    def align_chars(
        self,
        text: str,
        char_offsets: tuple[int, ...],
        audio_file_path: Path,
    ) -> tuple[float, ...]:
        duration = audio.get_duration(audio_file_path)
        timestamps = tuple(
            round(duration * offset / len(text), 3) for offset in char_offsets
        )
        return timestamps

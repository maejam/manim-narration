from pathlib import Path

from manim_narration import audio_utils as audio

from .aligner_base import AlignmentService


class Interpolator(AlignmentService):
    """A very basic implementation to map character offsets to timestamps."""

    def align_chars(
        self,
        raw_text: str,
        char_offsets: tuple[int, ...],
        audio_file_path: Path,
    ) -> tuple[float, ...]:
        duration = audio.get_duration(audio_file_path)
        timestamps = tuple(duration * offset / len(raw_text) for offset in char_offsets)
        return timestamps

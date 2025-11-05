from pathlib import Path

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
        audio_duration: float,
    ) -> tuple[float, ...]:
        timestamps = tuple(
            round(audio_duration * offset / len(text), 3) for offset in char_offsets
        )
        return timestamps

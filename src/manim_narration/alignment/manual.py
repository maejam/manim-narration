from pathlib import Path

from .aligner_base import AlignmentService


class ManualAligner(AlignmentService):
    """Do not perform any alignment, letting the user manually align text and speech.

    Returns
    -------
    A tuple mapping each character offset to the very beginning of the speech.

    """

    def align_chars(
        self,
        raw_text: str,
        char_offsets: tuple[int, ...],
        audio_file_path: Path,
    ) -> tuple[float, ...]:
        return (0,) * len(char_offsets)

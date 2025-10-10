from abc import ABC, abstractmethod
from pathlib import Path

from manim_narration._config.config_base import Config
from manim_narration.tags import TagParser
from manim_narration.typing import all_strings
from manim_narration.utils import NarrationError


class AlignmentError(NarrationError): ...


class AlignmentService(ABC, Config):
    """Define the functionality common to all alignment services.

    To define a concrete AlignmentService procede as follows:
    1. Inherit from this class.
    2. Provide an implementation for all abstract methods.

    See the Interpolator service implementation for a basic example.
    """

    @abstractmethod
    def align_chars(
        self, raw_text: str, char_offsets: tuple[int, ...], audio_file_path: Path
    ) -> tuple[float, ...]:
        """Align character offsets from the original text with the generated speech.

        Concrete alignment services must provide an implementation for this method.

        Parameters
        ----------
        raw_text
            The original text including the tags.
        char_offsets
            A tuple of character offsets in the text to align with the audio speech.
        audio_file_path
            The path to the audio file containing the generated speech.

        Returns
        -------
        A tuple of float timestamps relative to the beginning of the speech in seconds
        corresponding to each character offset.

        """
        raise NotImplementedError

    def _align_bookmarks(
        self, raw_text: str, audio_file_path: Path
    ) -> dict[str, float]:
        """Retrieve the timestamps for each bookmark in the text.

        Parameters
        ----------
        raw_text
            The original text including the tags.
        audio_file_path
            The path to the audio file containing the generated speech.

        Returns
        -------
        A dictionary mapping each bookmark mark attribute to its timestamp in the audio.

        """
        bookmark_mapping = self.config.tags.mapping["bookmark"]
        parser = TagParser(tags_to_record={bookmark_mapping})
        parser.feed(raw_text)

        if any(tag.kind != "startend" for tag in parser.tags):
            raise AlignmentError(
                "Bookmarks should be self-closing tags (e.g. `<bookmark mark='A' />)`"
            )

        marks = [tag.attrs.get("mark") for tag in parser.tags]
        if len(marks) != len(set(marks)):
            raise AlignmentError("Each bookmark should have a unique name.")

        if not all_strings(marks):
            raise AlignmentError("Bookmarks must define a mark attribute.")

        bk_tuple = self.align_chars(
            parser.text, tuple(tag.offset for tag in parser.tags), audio_file_path
        )

        bk_dict = dict(zip(marks, bk_tuple, strict=True))

        return bk_dict

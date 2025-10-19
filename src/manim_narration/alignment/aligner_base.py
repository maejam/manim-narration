import json
import typing as t
from abc import ABC, abstractmethod
from pathlib import Path

import manim_narration.utils as utils
from manim_narration._config.config_base import Config
from manim_narration.tags import TagParser
from manim_narration.typing import AlignmentData, all_strings

logger = utils.get_logger(__name__)


class AlignmentError(utils.NarrationError): ...


class AlignmentService(ABC, Config):
    """Define the functionality common to all alignment services.

    To define a concrete AlignmentService procede as follows:
    1. Inherit from this class.
    2. Provide an implementation for all abstract methods.
    3. Optionally provide implementation for any method that is not abstract and does
       not start with an underscore.
    4. If you override the `__init__` method, do not forget to call `super()` and
       provide all the calling arguments as keyword arguments.

    See the Interpolator service implementation for a (very) basic example.

    Parameters
    ----------
    service_kwargs
        All the arguments used when instantiating the service. Used to create the
        `AlignmentData` dictionary.

    """

    def __init__(self, **service_kwargs: t.Any) -> None:
        self.service_kwargs = service_kwargs

    @abstractmethod
    def align_chars(
        self, text: str, char_offsets: tuple[int, ...], audio_file_path: Path
    ) -> tuple[float, ...]:
        """Align character offsets from the original text with the generated speech.

        Concrete alignment services must provide an implementation for this method.

        Parameters
        ----------
        text
            The spoken text without the tags.
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

    def _align_chars_and_cache(
        self,
        text: str,
        char_offsets: tuple[int, ...],
        audio_file_path: Path,
        alignment_data: AlignmentData,
    ) -> tuple[float, ...]:
        """Manage cache with character alignment.

        This function is a wrapper around `align_chars`. It first checks if the
        requested alignment is already cached. If not, it calls the alignment service
        and then caches the data.

        Parameters
        ----------
        text
            The spoken text without the tags.
        char_offsets
            A tuple of character offsets in the text to align with the audio speech.
        audio_file_path
            The path to the audio file containing the generated speech.
        alignment_data
            The `typing.AlignmentData` instance representing this alignment process.

        Returns
        -------
        A tuple of float timestamps relative to the beginning of the speech in seconds
        corresponding to each character offset.

        """
        # check cached data
        json_file_base_name = utils.get_hash_from_data(
            alignment_data, self.config.cache.hash_algo, self.config.cache.hash_len
        )
        json_file_path = (audio_file_path.parent / json_file_base_name).with_suffix(
            ".json"
        )
        if json_file_path.exists():
            logger.info(f"Returning alignment from cache: '{json_file_path}'")
            with json_file_path.open() as json_file:
                return tuple(json.load(json_file))

        # call concrete service
        aligned_tuple = self.align_chars(text, char_offsets, audio_file_path)

        # serialize to cache
        with json_file_path.open("w") as json_file:
            json.dump(aligned_tuple, json_file)

        logger.info(f"Alignment saved to: '{json_file_path}'")

        return aligned_tuple

    def _align_bookmarks(
        self,
        raw_text: str,
        audio_file_path: Path,
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
        alignment_data: AlignmentData = {
            "raw_text": raw_text,
            "service_name": type(self).__name__,
            "service_kwargs": self.service_kwargs,
        }
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

        logger.info(f"Aligning bookmarks: {[tag.attrs['mark'] for tag in parser.tags]}")

        # Get alignment from cache if already generated else generate and cache
        bk_tuple = self._align_chars_and_cache(
            parser.text,
            tuple(tag.offset for tag in parser.tags),
            audio_file_path,
            alignment_data,
        )

        bk_dict = dict(zip(marks, bk_tuple, strict=True))
        return bk_dict

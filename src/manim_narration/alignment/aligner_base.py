import json
import typing as t
from abc import ABC, abstractmethod
from pathlib import Path

import manim_narration.utils as utils
from manim_narration._config.config_base import Config
from manim_narration.tags import TagParser
from manim_narration.typing import BookmarksData, all_strings


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

    See the Interpolator service implementation for a basic example.

    Parameters
    ----------
    service_kwargs
        All the arguments used when instantiating the service. Used to create the
        `BookmarksData` dictionary.

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

        # Get alignment from cache if already generated
        bookmarks_data: BookmarksData = {
            "raw_text": raw_text,
            "service_name": type(self).__name__,
            "service_kwargs": self.service_kwargs,
        }
        json_file_base_name = utils.get_hash_from_data(
            bookmarks_data, self.config.cache.hash_algo, self.config.cache.hash_len
        )
        json_file_path = (audio_file_path.parent / json_file_base_name).with_suffix(
            ".json"
        )
        if json_file_path.exists():
            with json_file_path.open() as json_file:
                return t.cast(dict[str, t.Any], json.load(json_file))

        # call concrete service
        bk_tuple = self.align_chars(
            parser.text, tuple(tag.offset for tag in parser.tags), audio_file_path
        )

        bk_dict = dict(zip(marks, bk_tuple, strict=True))

        # serialize to cache
        with json_file_path.open("w") as json_file:
            json.dump(bk_dict, json_file)

        return bk_dict

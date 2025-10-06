import typing as t
from abc import ABC, abstractmethod
from pathlib import Path

from manim_narration import utils
from manim_narration._config.base import Config
from manim_narration.typing import SpeechData


class SpeechServiceError(utils.NarrationError):
    """Errors occuring during the Text To Speech process."""

    pass


class SpeechService(ABC, Config):
    """Define the functionality common to all speech services.

    To define a concrete SpeechService procede as follows:
    1. Inherit from this class.
    2. Provide an implementation for all abstract methods.
    3. Optionally provide implementation for any method that is not abstract and does
       not start with an underscore.
    4. If you override the `__init__` method, do not forget to call `super()` and
       provide all the calling arguments as keyword arguments.

    See the ggts service implementation for an example.

    Parameters
    ----------
    service_kwargs
        All the arguments used when instantiating the service. Used to create the
        `SpeechData` dictionary.

    """

    def __init__(
        self, create_subcaption: bool = False, **service_kwargs: t.Any
    ) -> None:
        self.service_kwargs = service_kwargs
        self.create_subcaption = create_subcaption

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Define the extension suffix for the audio files.

        Returns
        -------
        The extension suffix, including the dot (e.g.: `return ".mp3"`)

        """
        raise NotImplementedError

    @abstractmethod
    def generate_speech(self, text: str, audio_file_path: Path) -> Path:
        """Generate the audio file containing the speech from the given text.

        Each concrete service should implement this method.

        Parameters
        ----------
        text
            The text to synthesize speech from.

        audio_file_path
            The path to save the audio file to.

        Returns
        -------
        The path to the generated audio file.

        """
        raise NotImplementedError

    def audio_callback(self, audio_file_path: Path) -> Path:
        """Modify the audio file after it has been genereated and saved to disk.

        Override this method to do something with the audio file, e.g. noise reduction.

        Parameters
        ----------
        audio_file_path
            The path to the audio file.

        Returns
        -------
        The path to the modified audio file.

        """
        return audio_file_path

    def _get_speech(self, text: str) -> Path:
        """Orchestrate the speech generation.

        This method is a wrapper around `generate_speech` and is called from the scene
        object.

        Parameters
        ----------
        text
            The tag free text to synthesize speech from.

        Returns
        -------
        The Path to the generated audio file.

        """
        # Get audio from cache if already generated
        speech_data: SpeechData = {
            "input_text": text,
            "service_name": type(self).__name__,
            "service_kwargs": self.service_kwargs,
        }
        filename = self.config.cache.audio_file_base_name + self.file_extension
        audio_file_path = self._get_path_to_file_in_cache(speech_data, filename)
        if audio_file_path.exists():
            return audio_file_path
        else:
            audio_file_path.parent.mkdir(parents=True)

        # Preprocessing
        text = " ".join(text.split())  # remove newlines and multiple consecutive spaces

        # Call concrete service
        audio_file_path = self.generate_speech(text, audio_file_path)

        # Postprocessing
        audio_file_path = self.audio_callback(audio_file_path)

        return audio_file_path

    def _get_path_to_file_in_cache(
        self, speech_data: SpeechData, filename: str
    ) -> Path:
        """Compute the path to a file in the cache directory.

        The actual file may or may not exist yet.

        Parameters
        ----------
        speech_data
            The SpeechData dictionary.
        filename
            The name of the file whose path to return.

        Returns
        -------
        The path to the file.

        """
        dir_in_cache = utils.get_hash_from_data(
            speech_data, self.config.cache.hash_algo, self.config.cache.hash_len
        )
        file_path = Path(self.config.cache.dir) / dir_in_cache / filename
        return file_path

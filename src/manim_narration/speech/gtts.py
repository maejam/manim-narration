import typing as t
from pathlib import Path

import gtts

from manim_narration.speech.speech_base import SpeechService, SpeechServiceError


class GTTSService(SpeechService):
    """Generate speech with Google Translate's Text-to-Speech API.

    See the gTTS documentation: <https://gtts.readthedocs.io/en/latest/>
    for more information.

    Parameters
    ----------
    lang
        The language to use for the speech.
    tld
        Top level domain. Can be used to change the acccent.
    create_subcaption
        Whether this service should create subcaptions or not.
    kwargs
        Other keyword arguments passed to gtts. See the documentation for more
        information.

    """

    def __init__(
        self,
        lang: str = "en",
        tld: str = "com",
        create_subcaption: bool = False,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(create_subcaption, lang=lang, tld=tld, **kwargs)
        self.lang = lang
        self.tld = tld
        self.kwargs = kwargs

    @property
    def file_extension(self) -> str:
        """GTTS generates mp3 files."""
        return ".mp3"

    def generate_speech(self, text: str, audio_file_path: Path) -> Path:
        """Generate speech with gTTS."""
        try:
            tts = gtts.gTTS(text, tld=self.tld, lang=self.lang, **self.kwargs)
        except gtts.gTTSError as e:
            raise SpeechServiceError(
                f"""Failed to initialize gTTS. Are you sure the arguments are correct?
                lang: {self.lang},
                tld: {self.tld},
                {self.kwargs}.
                See the documentation: <https://gtts.readthedocs.io/en/latest/>."""
            ) from e

        try:
            tts.save(audio_file_path)
        except gtts.gTTSError as e:
            raise SpeechServiceError(
                f"""gTTS gave an error when saving the file.
                audio file path: {audio_file_path}
                See the documentation: <https://gtts.readthedocs.io/en/latest/>."""
            ) from e

        return audio_file_path

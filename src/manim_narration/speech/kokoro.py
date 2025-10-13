import typing as t
from pathlib import Path

import soundfile as sf
from kokoro import KPipeline

from .speech_base import SpeechService


class KokoroService(SpeechService):
    """Generate speech with Kokoro.

    https://huggingface.co/hexgrad/Kokoro-82M
    https://github.com/hexgrad/kokoro

    """

    def __init__(
        self,
        lang_code: str,
        voice: str,
        create_subcaption: bool = False,
        **service_kwargs: t.Any,
    ) -> None:
        super().__init__(
            create_subcaption, lang_code=lang_code, voice=voice, **service_kwargs
        )
        self.pipeline = KPipeline(lang_code=lang_code)
        self.voice = voice

    @property
    def file_extension(self) -> str:
        return ".wav"

    def generate_speech(self, text: str, audio_file_path: Path) -> Path:
        generator = self.pipeline(text, voice=self.voice)
        for _, _, audio in generator:
            sf.write(audio_file_path, audio, 24000)
        return audio_file_path

import typing as t
from pathlib import Path

import torch
from TTS.api import TTS  # type:ignore[import-untyped]

from .speech_base import SpeechService


class CoquiService(SpeechService):
    """Generate speech with coqui-tts.

    The original coqui-ai project being discontinued, this fork is used instead:
    repo: https://github.com/idiap/coqui-ai-TTS
    documentation: https://coqui-tts.readthedocs.io/en/latest/

    For more information on the available models and their specific parameters, see the
    links above. The code is open-source (MPL2.0) but some models are not available for
    commercial use, especially the XTTS models. More information on the models licenses:
    https://github.com/idiap/coqui-ai-TTS/blob/dev/TTS/.models.json

    You can list the models in the command line using `tts list_models`.
    List the speakers for a model: `tts --model_name <model_name> --list_speaker_idxs`
    List the languages for a model: `tts --model_name <model_name> --list_language_idxs`

    Parameters
    ----------
    model
        The model used to generate the speech.
    create_subcaption
        Whether this service should create subcaptions or not.
    kwargs
        Other keyword arguments passed to the model. See the documentation for more
        information.

    """

    def __init__(
        self,
        model: str,
        create_subcaption: bool = False,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(
            create_subcaption,
            model=model,
            **kwargs,
        )
        self.model = model
        self.kwargs = kwargs
        self.is_speaker_wav_cached = False

        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS(self.model).to(device)

    @property
    def file_extension(self) -> str:
        return ".wav"

    def generate_speech(self, text: str, audio_file_path: Path) -> Path:
        kwargs = {
            "text": text,
            "file_path": audio_file_path,
        }
        kwargs.update(self.kwargs)

        if self.kwargs.get("speaker_wav") and self.is_speaker_wav_cached:
            del self.kwargs["speaker_wav"]

        self.tts.tts_to_file(**kwargs)
        self.is_speaker_wav_cached = True
        return audio_file_path

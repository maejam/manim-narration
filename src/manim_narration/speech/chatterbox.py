import typing as t
from pathlib import Path

import torch
import torchaudio as ta
from chatterbox import ChatterboxMultilingualTTS, ChatterboxTTS

from .speech_base import SpeechService


class ChatterboxService(SpeechService):
    """Generate speech with Chatterbox.

    https://github.com/resemble-ai/chatterbox

    """

    def __init__(
        self,
        language_id: str = "en",
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        audio_prompt_path: str | None = None,
        repetition_penalty: float = 1.2,
        min_p: float = 0.05,
        top_p: float = 1.0,
        temperature: float = 0.8,
        **service_kwargs: t.Any,
    ) -> None:
        super().__init__(
            language_id=language_id,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight,
            audio_prompt_path=audio_prompt_path,
            repetition_penalty=repetition_penalty,
            min_p=min_p,
            top_p=top_p,
            temperature=temperature,
            **service_kwargs,
        )

        # Automatically detect the best available device
        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"

        self.language_id = language_id
        self.exaggeration = exaggeration
        self.cfg_weight = cfg_weight
        self.audio_prompt_path = audio_prompt_path
        self.repetition_penalty = repetition_penalty
        self.min_p = min_p
        self.top_p = top_p
        self.temperature = temperature
        self.kwargs = service_kwargs

    @property
    def file_extension(self) -> str:
        return ".wav"

    def generate_speech(self, text: str, audio_file_path: Path) -> Path:
        if self.language_id == "en":
            model = ChatterboxTTS.from_pretrained(device=self.device)
            wav = model.generate(
                text=text,
                repetition_penalty=self.repetition_penalty,
                min_p=self.min_p,
                top_p=self.top_p,
                audio_prompt_path=self.audio_prompt_path,
                exaggeration=self.exaggeration,
                cfg_weight=self.cfg_weight,
                temperature=self.temperature,
            )
        else:
            model = ChatterboxMultilingualTTS.from_pretrained(
                device=torch.device(self.device)
            )
            wav = model.generate(
                text=text,
                repetition_penalty=self.repetition_penalty,
                min_p=self.min_p,
                top_p=self.top_p,
                audio_prompt_path=self.audio_prompt_path,
                exaggeration=self.exaggeration,
                cfg_weight=self.cfg_weight,
                temperature=self.temperature,
                language_id=self.language_id,
            )

        ta.save(audio_file_path, wav, model.sr)
        return audio_file_path

import typing as t
from pathlib import Path

import torch
from ctc_forced_aligner import (
    generate_emissions,
    get_alignments,
    get_spans,
    load_alignment_model,
    load_audio,
    postprocess_results,
    preprocess_text,
)

from .aligner_base import AlignmentService


class CTCAligner(AlignmentService):
    """Align text to speech using CTC based models.

    This aligner is powered by:
    https://github.com/MahmoudAshraf97/ctc-forced-aligner/tree/main

    To learn more about the CTC architecture, see:
    https://huggingface.co/learn/audio-course/chapter3/ctc

    Pretrained Wav2Vec2, HuBERT, and MMS models from HuggingFace can be used. See:
    https://huggingface.co/models?pipeline_tag=automatic-speech-recognition&sort=downloads

    The default model is under the CC-BY-NC-4.0 license, which prohibits commercial use.
    Please, consider starring the project on Github if you find it useful.

    Parameters
    ----------
    language
        The ISO-639-3 code. See: https://en.wikipedia.org/wiki/List_of_ISO_639-3_codes
    model_id
        The HuggingFace model_id to be used. See:
        https://huggingface.co/models?pipeline_tag=automatic-speech-recognition&sort=downloads

    batch_size
        The size of a batch of data forwarded to the model. No need to change it in most
        cases.
    kwargs
        Other keyward arguments forwarded to the base Aligner.

    Returns
    -------
    A tuple containing the computed timestamps for each bookmark in the original text.

    """

    def __init__(
        self,
        language: str,
        model_id: str = "MahmoudAshraf/mms-300m-1130-forced-aligner",
        batch_size: int = 16,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(
            language=language, model_id=model_id, batch_size=batch_size, **kwargs
        )
        self.language = language
        self.model_id = model_id
        self.batch_size = batch_size

    def align_chars(
        self, text: str, char_offsets: tuple[int, ...], audio_file_path: Path
    ) -> tuple[float, ...]:
        device = "cuda" if torch.cuda.is_available() else "cpu"

        alignment_model, alignment_tokenizer = load_alignment_model(
            device,
            model_path=self.model_id,
            dtype=torch.float16 if device == "cuda" else torch.float32,
        )

        audio_waveform = load_audio(
            str(audio_file_path), alignment_model.dtype, alignment_model.device
        )

        emissions, stride = generate_emissions(
            alignment_model, audio_waveform, batch_size=self.batch_size
        )

        tokens_starred, text_starred = preprocess_text(
            text, romanize=True, language=self.language, split_size="char"
        )

        segments, scores, blank_token = get_alignments(
            emissions,
            tokens_starred,
            alignment_tokenizer,
        )

        spans = get_spans(tokens_starred, segments, blank_token)

        timestamps = postprocess_results(text_starred, spans, stride, scores)
        return tuple(timestamps[i]["start"] for i in char_offsets)

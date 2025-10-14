import timeit
import typing as t
from pathlib import Path

import tabulate

from manim_narration.audio_utils import convert_to_wav
from manim_narration.speech import (
    CoquiService,
    GTTSService,
    KokoroService,
)
from manim_narration.speech.speech_base import SpeechService

SPEECH_SERVICES = [
    CoquiService(
        "tts_models/multilingual/multi-dataset/your_tts",
        language="en",
        speaker="female-en-5",
    ),
    GTTSService(),
    KokoroService(),
]
NUM_EXECUTIONS = 10
TEXT = (
    "Narration is the use of a written or spoken commentary"
    "to convey a story to an audience."
)


speech_service: SpeechService


def benchmark_speech_service() -> None:
    path = Path().cwd() / f"benchmarks/narrations/{type(speech_service).__name__}"
    path.parent.mkdir(exist_ok=True)
    file = speech_service.generate_speech(
        TEXT, path.with_suffix(speech_service.file_extension)
    )
    # convert to wav because it is part of the speech generation process
    file = convert_to_wav(file)


def build_markdown() -> t.Generator[list[list[str]], list[str], None]:
    data: list[list[str]] = []
    while True:
        new_line: list[str] = yield data
        data.append(new_line)


if __name__ == "__main__":
    markdown_generator: t.Generator[list[list[str]], list[str], None] = build_markdown()
    next(markdown_generator)
    md = []

    for speech_service in SPEECH_SERVICES:
        # time speech generation
        res = timeit.timeit(
            benchmark_speech_service,
            globals={"speech_service": speech_service},
            number=NUM_EXECUTIONS,
        )

        # send result to build_markdown
        service_name = type(speech_service).__name__
        md = markdown_generator.send(
            [
                service_name[:-7],
                "",
                "",
                f"{round(res / NUM_EXECUTIONS, 2)} seconds",
                f"[sample](benchmarks/narrations/{service_name}.wav?raw=True)",
            ]
        )

    headers = [
        "Service",
        "type".ljust(5),
        "Languages".ljust(20),
        "Inference time (cpu)",
        "Audio sample",
    ]
    md_table = tabulate.tabulate(
        md,
        headers=headers,
        tablefmt="github",
    )
    print(md_table)

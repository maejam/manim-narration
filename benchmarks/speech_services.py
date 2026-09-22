import pickle
import shutil
import time
import typing as t
from pathlib import Path

import tabulate

from manim_narration import NarrationScene, config
from manim_narration.speech import (
    ChatterboxService,
    CoquiService,
    GTTSService,
    KokoroService,
)
from manim_narration.tracker import NarrationTracker

path = Path(__file__).parent / "narrations/temp/"
path.mkdir(exist_ok=True, parents=True)
config.cache.dir = path

MULTITHREADING_MAX_WORKERS = 3
MULTIPROCESSING_MAX_WORKERS = 2

SPEECH_SERVICES = {
    "coqui": CoquiService(
        "tts_models/multilingual/multi-dataset/xtts_v2",
        language="en",
        speaker="Claribel Dervla",
    ),
    "gtts": GTTSService(),
    "kokoro": KokoroService(),
    "chatterbox": ChatterboxService(language_id="en"),
}
EXECUTION_MODES: list[t.Literal["sequential", "multithreading", "multiprocessing"]] = [
    "sequential",
    "multithreading",
    # "multiprocessing",
]
TEXTS = [
    "Narration number one",
    "Narration number two",
    "Narration number three",
    "Narration number four",
    "Narration number five",
    "Narration number six",
    "Narration number seven",
    "Narration number eight",
    "Narration number nine",
    "Narration number ten",
]

scene = NarrationScene()
scene.set_speech_services(**SPEECH_SERVICES)


def benchmark_speech_service(
    speech_service_id: str,
    mode: t.Literal["sequential", "multithreading", "multiprocessing"],
) -> float:
    speech_service = SPEECH_SERVICES[speech_service_id]
    print(
        f"\n=============== Benchmarking: {type(speech_service).__name__[:-7]} / {mode}"
        " ==============="
    )
    max_workers = (
        MULTITHREADING_MAX_WORKERS
        if mode == "multithreading"
        else MULTIPROCESSING_MAX_WORKERS
    )
    t1 = time.perf_counter()
    tasks = {f"task{i}": text for i, text in enumerate(TEXTS)}

    results = scene.generate_narrations(
        speech_service_id,
        mode=mode,
        max_workers=max_workers,
        ignore_cache=True,
        **tasks,  # pyright: ignore[reportArgumentType]
    )

    t2 = time.perf_counter()
    duration = t2 - t1
    for k, v in results.items():
        assert k.startswith("task")
        assert isinstance(v, NarrationTracker)
        assert v.audio_file_path.suffix == ".wav"
    print(f"{len(tasks)} narrations generated in {duration} seconds.")
    return duration


def build_markdown() -> t.Generator[list[list[str]], list[str], None]:
    data: list[list[str]] = []
    while True:
        new_line: list[str] = yield data
        data.append(new_line)


if __name__ == "__main__":
    markdown_generator: t.Generator[list[list[str]], list[str], None] = build_markdown()
    next(markdown_generator)
    md = []

    for speech_service_id in SPEECH_SERVICES:
        times = []
        for mode in EXECUTION_MODES:
            try:
                res: float | str = benchmark_speech_service(speech_service_id, mode)
            except (pickle.PicklingError, OSError) as e:
                res = "NA"
                print(f"{mode} execution is not supported for this speech service: ", e)

            times.append(res)

        # send result to build_markdown
        speech_service = SPEECH_SERVICES[speech_service_id]
        service_name = type(speech_service).__name__[:-7]
        mean_times = []
        for time_ in times:
            try:
                mean_times.append(str(round(time_ / len(TEXTS), 2)))  # type: ignore[operator]
            except TypeError:  # "NA"
                mean_times.append("NA")

        md = markdown_generator.send(
            [
                service_name,
                "",
                "",
                " / ".join(mean_times),
                f"[sample](benchmarks/narrations/{service_name}.wav?raw=True)",
            ]
        )

    headers = [
        "Service",
        "type".ljust(5),
        "Languages".ljust(20),
        "Inference time (cpu)\\*",
        "Audio sample",
    ]
    md_table = tabulate.tabulate(
        md,
        headers=headers,
        tablefmt="github",
    )
    # delete temp dir
    shutil.rmtree(path, ignore_errors=True)
    print("\n\n", md_table)
    print(
        f"<sub>\\*Mean time in seconds to generate {len(TEXTS)} short speeches "
        f"({'/'.join(EXECUTION_MODES)})</sub>"
    )

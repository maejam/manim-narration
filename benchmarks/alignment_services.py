# the TRUTH tuple was adjusted using audacity
# the InterpolationAligner is pretty much instantaneaous, except for the initial
# overhead to compute the audio duration. This is then cached and would already be
# cached in a real usage of the library when the aligner is called.
import math
import timeit
import typing as t
from itertools import count
from pathlib import Path

import tabulate

from manim_narration.alignment import CTCAligner, InterpolationAligner, ManualAligner
from manim_narration.alignment.aligner_base import AlignmentService
from manim_narration.tags import TagParser

ALIGNMENT_SERVICES = [ManualAligner(), InterpolationAligner(), CTCAligner("eng")]
NUM_EXECUTIONS = 10
AUDIO_FILE = Path().cwd() / "benchmarks/reference_speech.wav"
DURATION = 56.424
TEXT = (
    'From Wikipedia: <bookmark mark="narration"/>Narration is the use of a written '
    'or spoken commentary to convey a story to an <bookmark mark="audience"/>audience. '
    'Narration is conveyed by a <bookmark mark="narrator"/>narrator: a specific person,'
    " or unspecified literary voice, developed by the creator of the story to deliver "
    "information to the audience, particularly about the plot: the series of events. "
    'Narration is a required element of all written stories (<bookmark mark="novels"/>'
    'novels, <bookmark mark="short_stories"/>short stories, <bookmark mark="poems"/>'
    'poems, <bookmark mark="memoirs"/>memoirs, etc.), presenting the story in its '
    "entirety. It is optional in most other storytelling formats, such as films, "
    "plays, television shows and video games, in which the story can be conveyed "
    'through other means, <bookmark mark="the_end"/>like dialogue between '
    "characters or visual action."
)
TRUTH = (1.958, 6.930, 10.012, 29.470, 30.697, 32.461, 33.654, 52.503)

alignment_service: AlignmentService
results: list[float] = [0.0] * len(ALIGNMENT_SERVICES)


def benchmark_alignment_service() -> None:
    parser = TagParser()
    parser.feed(TEXT)
    char_offsets = tuple(tag.offset for tag in parser.tags)
    aligned = alignment_service.align_chars(
        parser.text, char_offsets, AUDIO_FILE, DURATION
    )
    distances = tuple((al - tr) ** 2 for al, tr in zip(aligned, TRUTH, strict=True))
    distance = math.sqrt(sum(distances))

    global results
    results[idx] = distance


def build_markdown() -> t.Generator[list[list[str]], list[str], None]:
    data: list[list[str]] = []
    while True:
        new_line: list[str] = yield data
        data.append(new_line)


if __name__ == "__main__":
    markdown_generator: t.Generator[list[list[str]], list[str], None] = build_markdown()
    next(markdown_generator)
    md = []
    counter = count()

    for alignment_service in ALIGNMENT_SERVICES:
        idx = next(counter)
        # time alignment generation
        res = timeit.timeit(
            benchmark_alignment_service,
            globals={"alignment_service": alignment_service, "idx": idx},
            number=NUM_EXECUTIONS,
        )

        # send result to build_markdown
        service_name = type(alignment_service).__name__
        md = markdown_generator.send(
            [
                service_name[:-7],
                "",
                "",
                f"{round(res / NUM_EXECUTIONS, 2)} seconds",
                str(results[idx]),
            ]
        )

    headers = [
        "Service",
        "Description/Links".ljust(50),
        "type".ljust(5),
        "Inference time (cpu)",
        "Distance from truth",
    ]
    md_table = tabulate.tabulate(
        md,
        headers=headers,
        tablefmt="github",
    )
    print(md_table)

from pathlib import Path

import pytest

from manim_narration.alignment import ManualAligner


@pytest.mark.parametrize(
    ("offsets", "expected"),
    [
        ((0,), (0,)),
        ((25,), (0,)),
        ((0, 25), (0, 0)),
        ((5, 10, 15, 20), (0, 0, 0, 0)),
        ((), ()),
        ((0, 0, 0, 0), (0, 0, 0, 0)),
    ],
)
def test_manual_aligner(offsets, expected):
    ma = ManualAligner()
    assert ma.align_chars("This is a len(25) string.", offsets, Path()) == expected

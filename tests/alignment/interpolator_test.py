from pathlib import Path
from unittest.mock import patch

import pytest

from manim_narration.alignment import InterpolationAligner


@pytest.mark.parametrize(
    ("offsets", "duration", "expected"),
    [
        ((0,), 25, (0,)),  # bk in very beginning
        ((25,), 25, (25,)),  # bk at very end
        ((0, 25), 25, (0, 25)),  # both
        ((5, 10, 15, 20), 25, (5, 10, 15, 20)),
        ((5, 10, 15, 20), 12.5, (2.5, 5, 7.5, 10)),
        ((), 12.5, ()),
        ((0, 0, 0, 0), 0, (0, 0, 0, 0)),
    ],
)
def test_interpolator(offsets, duration, expected):
    i = InterpolationAligner()
    with patch("manim_narration.audio_utils.get_duration") as mock_get_duration:
        mock_get_duration.return_value = duration
        assert i.align_chars("This is a len(25) string.", offsets, Path()) == expected

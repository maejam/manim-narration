import sys
from pathlib import Path
from unittest import mock

import pytest

from manim_narration.alignment.aligner_base import AlignmentError
from manim_narration.tracker import NarrationTracker

pytestmark = pytest.mark.skipif(
    sys.version_info[:2] == (3, 10),
    reason="unittest.mock does a __gettatr__ lookup that changed with 3.11+."
    "3.10 raises AttributeError: module 'manim_narration' has no attribute tracker",
)


@pytest.fixture
def scene():
    class Scene: ...

    scene = Scene()
    scene.alignment_services = {"default": mock.Mock()}
    scene.alignment_services["default"]._align_bookmarks = mock.Mock()
    return scene


@pytest.fixture
def mock_get_duration():
    with mock.patch("manim_narration.tracker.get_duration") as mgd:
        yield mgd


@pytest.mark.parametrize(
    ("total_dur", "curr_time", "expected"),
    [
        (5, 1, 4),
        (5, 1.5, 3.5),
        (10, 10, 0),
        (1, 1.5, 0),
        (0, 1.5, 0),
        (5, 5, 0),
    ],
)
def test_remaining_duration(mock_get_duration, scene, total_dur, curr_time, expected):
    mock_get_duration.return_value = total_dur
    tracker = NarrationTracker(
        scene, 0, scene.alignment_services["default"], "", Path()
    )
    tracker.scene.time = curr_time
    assert tracker.remaining_duration == expected


@pytest.mark.parametrize(
    ("bk_ts", "current", "target", "expected"),
    [
        ({}, "_origin_", "_origin_", 0),
        ({"a": 0, "b": 1}, "_origin_", "a", 0),
        ({"a": 0, "b": 1}, "a", "a", 0),
        ({"a": 0, "b": 1}, "_origin_", "b", 1),
        ({"a": 0, "b": 1}, "a", "b", 1),
        ({"a": 0, "b": 1, "c": 5, "d": 3}, "a", "c", 5),
        ({"a": 0, "b": 1, "c": 5, "d": 3}, "a", "d", 3),
        ({"a": 0, "b": 1, "c": 5, "d": 3}, "d", "c", 2),
    ],
)
def test_duration_until_bookmark(
    mock_get_duration, scene, bk_ts, current, target, expected
):
    scene.alignment_services["default"]._align_bookmarks.return_value = bk_ts
    tracker = NarrationTracker(
        scene, 0, scene.alignment_services["default"], "", Path()
    )
    tracker.current_bookmark = current
    assert tracker.duration_until_bookmark(target) == expected


@pytest.mark.parametrize(
    ("bk_ts", "current", "target", "error"),
    [
        ({"a": 0, "b": 1}, "_origin_", "origin_", "origin_"),
        ({"a": 0, "b": 1}, "a", "c", "c"),
        ({"a": 0, "b": 1, "c": 5, "d": 3}, "c", "e", "e"),
    ],
)
def test_duration_until_bookmark_with_unknown_bk_raises(
    mock_get_duration, scene, bk_ts, current, target, error
):
    scene.alignment_services["default"]._align_bookmarks.return_value = bk_ts
    tracker = NarrationTracker(
        scene, 0, scene.alignment_services["default"], "", Path()
    )
    tracker.current_bookmark = current
    with pytest.raises(AlignmentError, match=f"bookmark `{error}` does not exist"):
        tracker.duration_until_bookmark(target)

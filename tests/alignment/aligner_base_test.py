import pytest

from manim_narration.alignment.aligner_base import AlignmentError, AlignmentService


@pytest.fixture
def aligner():
    class Aligner(AlignmentService):
        def align_chars(
            self,
            text: str,
            char_offsets: tuple[int, ...],
            audio_file_path,
            audio_duration: float,
        ) -> tuple[float, ...]:
            return (0.0, 1.0, 1.5)

    return Aligner()


@pytest.mark.parametrize(
    "text",
    [
        "<bookmark mark='A'/>First one is good, but not this one: <bookmark mark='B'>",
        "<bookmark mark='A'/>First one is good, but not this one: </bookmark mark='B'>",
    ],
)
def test_align_bookmarks_raises_when_wrong_tag_kind(aligner, text, tmp_path):
    with pytest.raises(AlignmentError, match="should be self-closing"):
        aligner._align_bookmarks(text, tmp_path, 10.0)


@pytest.mark.parametrize(
    "text",
    [
        "<bookmark mark='A'/>First one is A, second also: <bookmark mark='A'/>",
    ],
)
def test_align_bookmarks_raises_when_same_names(aligner, text, tmp_path):
    with pytest.raises(AlignmentError, match="should have a unique name"):
        aligner._align_bookmarks(text, tmp_path, 10.0)


@pytest.mark.parametrize(
    "text",
    [
        "<bookmark mark='A'/>First one is good, but not this one: <bookmark/>",
        "<bookmark mark='A'/>First one is good, but not this one: <bookmark mar='B'/>",
    ],
)
def test_align_bookmarks_raises_when_no_mark_attribute(aligner, text, tmp_path):
    with pytest.raises(AlignmentError, match="must define a mark attribute"):
        aligner._align_bookmarks(text, tmp_path, 10.0)


@pytest.mark.parametrize(
    "text",
    [
        "<bookmark mark='A'/>Test <bookmark mark='B'/>string. <bookmark mark='C'/>",
        "  <bookmark mark='A'/>Test <bookmark mark='B'/>string. <bookmark mark='C'/>  ",
        "<bookmark mark='A'/><bookmark mark='B'/><bookmark mark='C'/>Test string.",
        "Test string.<bookmark mark='A'/><bookmark mark='B'/><bookmark mark='C'/>",
    ],
)
def test_align_bookmarks_returns_right_dict(aligner, text, tmp_path):
    assert aligner._align_bookmarks(text, tmp_path, 10.0) == {
        "A": 0.0,
        "B": 1.0,
        "C": 1.5,
    }

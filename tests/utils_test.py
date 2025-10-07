import pytest

import manim_narration.utils as u


def test_get_hash_from_data_with_dict_returns_hash():
    assert len(u.get_hash_from_data({}, "sha256", -1)) == 64


@pytest.mark.parametrize("data", [[], 2, ""])
def test_get_hash_from_data_with_unsupported_data_raises(data):
    with pytest.raises(NotImplementedError):
        u.get_hash_from_data(data, "sha256", -1)


def test_get_hash_from_data_with_same_dict_different_order_gives_same_hash():
    assert u.get_hash_from_data({"a": 1, "b": 2}, "sha256", -1) == u.get_hash_from_data(
        {"b": 2, "a": 1}, "sha256", -1
    )


@pytest.mark.parametrize(
    ("length", "expected"), [(-10, 64), (0, 64), (1, 1), (64, 64), (640, 64)]
)
def test_get_hash_from_data_length(length, expected):
    assert len(u.get_hash_from_data({}, "sha256", length)) == expected


@pytest.mark.parametrize(
    ("text", "chars", "expected"),
    [
        ("Hello world", "", ["Hello world"]),
        ("Hello world", ":", ["Hello world"]),
        ("", ":", [""]),
        ("", "", [""]),
        ("Hello, world.", ",.", ["Hello,", "world."]),
        ("Hello, world.", ",", ["Hello,", "world."]),
        ("Hello, world.", ".", ["Hello, world."]),
        ("Hello!!! World...", "!", ["Hello!!!", "World..."]),
        ("Hello!!! World...", "!.", ["Hello!!!", "World..."]),
        ("Hello!!! World...", ".", ["Hello!!! World..."]),
        ("Hello... World!", ".", ["Hello...", "World!"]),
    ],
)
def test_split_after_characters(text, chars, expected):
    assert u.split_after_characters(text, chars) == expected


@pytest.mark.parametrize(
    ("splits", "max_len", "expected"),
    [
        (
            ["It should", "regroup", "everything."],
            len("It should regroup everything."),
            ["It should regroup everything."],
        ),
        (
            ["Everything but", "the last", "word."],
            len("Everything but the last word.") - 1,
            ["Everything but the last", "word."],
        ),
        (["", "first split is", "empty."], 100, ["first split is empty."]),
        (["middle split", "", "is empty."], 100, ["middle split is empty."]),
        (["last split", "is empty.", ""], 100, ["last split is empty."]),
    ],
)
def test_regroup_splits(splits, max_len, expected):
    assert u.regroup_splits(splits, max_len) == expected

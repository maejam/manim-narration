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

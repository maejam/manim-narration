import importlib
from pathlib import Path

import pytest

import manim_narration
from manim_narration.config_ import CONFIG_FILE_NAME
from manim_narration.config_ import ManimNarrationConfig
from manim_narration.utils import get_hash_from_data
from manim_narration.utils import remove_tags


@pytest.fixture
def user_conf():
    path = Path(CONFIG_FILE_NAME)
    with path.open("w") as f:
        f.write("""
        [TEST]
        cache_dir = {media_dir}/test_dir
        json_file_name = other_name
        other_key = {not_a_manim_config_key}/test

        [TAGS]
        bookmark = bookmark
        tag = tag
        testtag = foo
        """)
    config = ManimNarrationConfig(CONFIG_FILE_NAME)
    importlib.reload(manim_narration.config_)
    yield config
    path.unlink()


def test_remove_tags_without_tags():
    text = "This is just a test string."
    assert remove_tags(text) == text


def test_remove_tags_with_malformed_tags():
    texts = [
        "This<bookmark> is just a test string.",  # no slash
        "And another/> < one>",
        "And yet<bookmark/> another one.",  # no space
        "",  # empty string
        "<bookmark/w>",
    ]
    for text in texts:
        assert remove_tags(text) == text


def test_remove_tags_does_not_remove_non_declared_tags():
    texts = [
        "This is <gghghg />a test.",
        "<gghghg />This is a test.",
        "This is a test.<gghghg />",
    ]
    for text in texts:
        assert remove_tags(text) == text


def test_remove_tags_works_with_only_one_tag():
    assert remove_tags("This is a <bookmark mark='test'/>.") == "This is a ."
    assert remove_tags("And another<bookmark />") == "And another"


def test_remove_tags_works_with_all_declared_tags(user_conf):
    assert remove_tags("It works<bookmark />!") == "It works!"
    # assert remove_tags("It works<tag />!") == "It works!"
    assert remove_tags("It works<foo />!") == "It works!"


def test_remove_tags_works_with_multiple_tags(user_conf):
    assert remove_tags("It <tag />really <tag />works!") == "It really works!"
    assert remove_tags("It <bookmark />works<foo />!") == "It works!"


def test_get_hash_from_data_with_dict_returns_hash():
    assert len(get_hash_from_data({}, "sha256")) == 64


def test_get_hash_from_data_with_non_dict_raises():
    with pytest.raises(NotImplementedError):
        get_hash_from_data([], "sha256")
    with pytest.raises(NotImplementedError):
        get_hash_from_data(2, "sha256")
    with pytest.raises(NotImplementedError):
        get_hash_from_data("", "sha256")


def test_get_hash_from_data_with_same_dict_differnt_order_gives_same_hash():
    assert get_hash_from_data({"a": 1, "b": 2}, "sha256") == get_hash_from_data(
        {"b": 2, "a": 1}, "sha256"
    )


def test_get_hash_from_data_len_works():
    assert len(get_hash_from_data({}, "sha256", 0)) == 64
    assert len(get_hash_from_data({}, "sha256", 1)) == 1
    assert len(get_hash_from_data({}, "sha256", 64)) == 64
    assert len(get_hash_from_data({}, "sha256", 640)) == 64

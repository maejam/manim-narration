from pathlib import Path

import manim as m
import pytest

from manim_narration.config_ import CONFIG_FILE_NAME
from manim_narration.config_ import ManimNarrationConfig
from manim_narration.config_ import NarrationConfigKeyError
from manim_narration.config_ import NarrationConfigPlaceHolderError


@pytest.fixture
def user_conf():
    path = Path(CONFIG_FILE_NAME)
    with path.open("w") as f:
        f.write("""
        [TEST]
        cache_dir = {media_dir}/test_dir
        json_file_name = other_name
        other_key = {not_a_manim_config_key}/test

        [TEST2]
        yet_another_key = yet_another_value
        cache_dir = not the good one
        """)
    config = ManimNarrationConfig(CONFIG_FILE_NAME)
    yield config
    path.unlink()


def test_original_config_file_is_read_by_default():
    config = ManimNarrationConfig(CONFIG_FILE_NAME)
    assert config._config["CACHE"]["json_file_name"] == "cache.json"


def test_user_config_file_is_read_if_exists(user_conf):
    assert user_conf._config["TEST"]["json_file_name"] == "other_name"


def test_dot_notation_access_to_config_values(user_conf):
    assert user_conf.json_file_name == "other_name"


def test_can_access_value_in_later_sections(user_conf):
    assert user_conf.yet_another_key == "yet_another_value"


def test_accessing_inexistant_config_value_raises_KeyError(user_conf):
    with pytest.raises(NarrationConfigKeyError, match="not_here"):
        user_conf.not_here


def test_placeholders_interpolation_in_config_values(user_conf):
    assert user_conf.cache_dir == f"{m.config.media_dir}/test_dir"


def test_accessing_config_value_with_inexistant_placeholder_raises_KeyError(user_conf):
    with pytest.raises(NarrationConfigPlaceHolderError, match="not_a_manim_config_key"):
        user_conf.other_key

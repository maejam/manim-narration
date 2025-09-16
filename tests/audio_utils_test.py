from pathlib import Path

import pytest

import manim_narration.audio_utils as audio
from manim_narration.config_ import config

config.cache_dir = Path(__file__).parent / "control_data"
AUDIO = "animating-technical-concepts-is-traditionally-b2cac437.mp3"
EMPTY_FILE = "empty.mp3"


def test_get_duration_audio_file():
    assert audio.get_duration(config.cache_dir / AUDIO) == 21.0


def test_get_duration_empty_audio_file_raises():
    with pytest.raises(audio.NarrationAudioError):
        audio.get_duration(config.cache_dir / EMPTY_FILE)

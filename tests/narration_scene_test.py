import pytest
import typing as t


from manim_narration import NarrationScene


# @pytest.fixture
# def scene():
#     class Scene(NarrationScene):
#         def add_narration(
#             self,
#             speech_service_id: str | None = None,
#             alignment_service_id: str | None = None,
#             *,
#             text: str = "",
#             create_subcaption: bool = False,
#             subcaption: str = "",
#             **subcaption_kwargs: t.Any,
#         ):
#             pass


def test_skip_narrations_no_section():
    from manim_narration import config

    config.skip_narrations = False
    config.skipped_narrations_duration = 2.0
    scene = NarrationScene()
    assert scene.current_section_skip_narrations is None
    assert scene.current_section_skipped_narrations_duration is None
    assert scene.skip_narrations is False
    assert scene.skipped_narrations_duration == 2.0

    config.skip_narrations = True
    config.skipped_narrations_duration = 5.0
    assert scene.current_section_skip_narrations is None
    assert scene.current_section_skipped_narrations_duration is None
    assert scene.skip_narrations is True
    assert scene.skipped_narrations_duration == 5.0


def test_skip_narrations_sections():
    from manim_narration import config

    config.skip_narrations = False
    config.skipped_narrations_duration = 2.0
    scene = NarrationScene()
    scene.next_section(skip_narrations=False, skipped_narrations_duration=2.0)
    assert scene.current_section_skip_narrations is False
    assert scene.current_section_skipped_narrations_duration == 2.0
    assert scene.skip_narrations is False
    assert scene.skipped_narrations_duration == 2.0

    scene.next_section(skip_narrations=True, skipped_narrations_duration=5.0)
    assert scene.current_section_skip_narrations is True
    assert scene.current_section_skipped_narrations_duration == 5.0
    assert scene.skip_narrations is True
    assert scene.skipped_narrations_duration == 5.0

    config.skip_narrations = True
    config.skipped_narrations_duration = 5.0
    scene = NarrationScene()
    scene.next_section(skip_narrations=False, skipped_narrations_duration=2.0)
    assert scene.current_section_skip_narrations is False
    assert scene.current_section_skipped_narrations_duration == 2.0
    assert scene.skip_narrations is False
    assert scene.skipped_narrations_duration == 2.0

    scene.next_section(skip_narrations=True, skipped_narrations_duration=5.0)
    assert scene.current_section_skip_narrations is True
    assert scene.current_section_skipped_narrations_duration == 5.0
    assert scene.skip_narrations is True
    assert scene.skipped_narrations_duration == 5.0

import inspect
import sys

import pytest


@pytest.fixture
def mn():
    pkg_name = "manim_narration"
    if pkg_name in sys.modules:
        del sys.modules[pkg_name]
    import importlib

    mn = importlib.import_module(pkg_name)
    yield mn
    if pkg_name in sys.modules:
        del sys.modules[pkg_name]


def test_config_is_not_instantiated_if_not_imported(mn):
    assert "config" not in mn.__dict__
    with pytest.raises(AttributeError):
        inspect.getattr_static(mn, "config")


def test_config_is_instantiated_when_imported(mn):
    assert "config" not in mn.__dict__
    config = mn.config
    assert "config" in mn.__dict__
    assert mn.__dict__["config"] is config


def test_subsequent_access_returns_same_instance(mn):
    first = mn.config
    second = mn.config
    third = mn.config
    assert first is second is third


def test_unknown_attribute_raises(mn):
    with pytest.raises(
        AttributeError,
        match="module 'manim_narration' has no attribute 'some_random_name",
    ):
        _ = mn.some_random_name

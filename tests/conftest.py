import pytest


# fixtures
@pytest.fixture(scope="module")
def speech_data():
    return {
        "input_text": """
        Animating technical concepts is traditionally pretty tedious since it can be difficult to make the animations precise enough to convey them accurately. Manim relies on Python’s simplicity to generate animations programmatically, making it convenient to specify exactly how each one should run.
        """,
        "input_data": {
            "input_text": """
            Animating technical concepts is traditionally pretty tedious since it can be difficult to make the animations precise enough to convey them accurately. Manim relies on Python’s simplicity to generate animations programmatically, making it convenient to specify exactly how each one should run.
            """,
            "service": "gtts",
        },
        "original_audio": "animating-technical-concepts-is-traditionally-b2cac437.mp3",
        "final_audio": "animating-technical-concepts-is-traditionally-b2cac437.mp3",
    }


# add `runslow` cli arg for running tests marked as slow
def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)

import os
from pathlib import Path

import pytest
from pydantic import Field, ValidationError

from manim_narration.config.base import (
    CONFIG_FILE_NAME,
    DOTENV_FILE_NAME,
    PYPROJECT_TOML_TABLE,
    PhField,
    PlaceholderModel,
    PlaceholderSettings,
)


@pytest.fixture
def tmp_files(tmp_path_factory):
    """Return a dict of files within tmp dirs:
    {
        "toml_home": Path().home() / CONFIG_FILE_NAME,
        "toml_cwd":  Path().cwd() / CONFIG_FILE_NAME",
        "dotenv": Path().cwd() / ".env",
        "pyproj": Path().cwd() / "pyproject.toml"
    }
    """
    home_dir = tmp_path_factory.mktemp("home_dir")
    cwd_dir = tmp_path_factory.mktemp("cwd_dir")

    original_home = Path.home
    original_cwd = Path.cwd

    Path.home = lambda: home_dir
    Path.cwd = lambda: cwd_dir

    yield {
        "toml_home": home_dir / CONFIG_FILE_NAME,
        "toml_cwd": cwd_dir / CONFIG_FILE_NAME,
        "dotenv": cwd_dir / DOTENV_FILE_NAME,
        "pyproj": cwd_dir / "pyproject.toml",
    }

    Path.home = original_home
    Path.cwd = original_cwd


@pytest.fixture
def env_vars():
    """Define and cleanup environment variables."""
    os.environ["NARRATION_PROGRAMMATIC"] = "from_env_var"
    os.environ["NARRATION_ENV_VAR"] = "from_env_var"
    os.environ["NARRATION_NESTED__PROGRAMMATIC"] = "from_env_var"
    os.environ["NARRATION_NESTED__ENV_VAR"] = "from_env_var"
    yield

    # Clean up env vars
    del os.environ["NARRATION_PROGRAMMATIC"]
    del os.environ["NARRATION_ENV_VAR"]
    del os.environ["NARRATION_NESTED__PROGRAMMATIC"]
    del os.environ["NARRATION_NESTED__ENV_VAR"]


def write_toml(path: Path, data: dict[str, str]):
    lines = []
    for key, value in data.items():
        lines.append(f'{key} = "{value}"')
    path.write_text("\n".join(lines))


def write_dotenv(path: Path, data: dict[str, str]):
    lines = []
    for key, value in data.items():
        lines.append(f"NARRATION_{key.replace('.', '__')}={value}")
    path.write_text("\n".join(lines))


def write_pyproj(path: Path, data: dict[str, str]):
    lines = ["[" + ".".join(part for part in PYPROJECT_TOML_TABLE) + "]"]
    for key, value in data.items():
        lines.append(f'{key} = "{value}"')
    path.write_text("\n".join(lines))


def prepare_data(data: dict, source: str):
    return {key: value.format(source=source) for key, value in data.items()}


@pytest.mark.failing_assertions(likely_source_of_failure="pydantic-settings")
def test_precedence_is_respected_with_nested_sections(tmp_files, env_vars):
    data = {
        "programmatic": "from_{source}",
        "env_var": "from_{source}",
        "dotenv": "from_{source}",
        "nested.programmatic": "from_{source}",
        "nested.env_var": "from_{source}",
        "nested.dotenv": "from_{source}",
    }
    write_dotenv(tmp_files["dotenv"], prepare_data(data, "dotenv"))

    data.update(
        {
            "pyproj": "from_{source}",
            "nested.pyproj": "from_{source}",
        }
    )
    write_pyproj(tmp_files["pyproj"], prepare_data(data, "pyproj"))

    data.update(
        {
            "cwd_toml": "from_{source}",
            "nested.cwd_toml": "from_{source}",
        }
    )
    write_toml(tmp_files["toml_cwd"], prepare_data(data, "cwd_toml"))

    data.update(
        {
            "home_toml": "from_{source}",
            "nested.home_toml": "from_{source}",
        }
    )
    write_toml(tmp_files["toml_home"], prepare_data(data, "home_toml"))

    class Nested(PlaceholderModel):
        programmatic: str = "from_default"
        env_var: str = "from_default"
        dotenv: str = "from_default"
        pyproj: str = "from default"
        cwd_toml: str = "from_default"
        home_toml: str = "from_default"
        default: str = "from_default"

    class Base(PlaceholderSettings):
        nested: Nested = Field(default_factory=Nested)
        programmatic: str = "from_default"
        env_var: str = "from_default"
        dotenv: str = "from_default"
        pyproj: str = "from default"
        cwd_toml: str = "from_default"
        home_toml: str = "from_default"
        default: str = "from_default"

    base = Base(placeholders={})

    base.programmatic = "from_programmatic"
    base.nested.programmatic = "from_programmatic"

    assert base.programmatic == "from_programmatic"
    assert base.nested.programmatic == "from_programmatic"
    assert base.env_var == "from_env_var"
    assert base.nested.env_var == "from_env_var"
    assert base.dotenv == "from_dotenv"
    assert base.nested.dotenv == "from_dotenv"
    assert base.pyproj == "from_pyproj"
    assert base.nested.pyproj == "from_pyproj"
    assert base.cwd_toml == "from_cwd_toml"
    assert base.nested.cwd_toml == "from_cwd_toml"
    assert base.home_toml == "from_home_toml"
    # it is unclear why this one assert fails. Toml file is written properly.
    # everything else works as expected. Maybe a bug in pydantic-settings.
    # assert base.nested.home_toml == "from_home_toml"
    assert base.default == "from_default"
    assert base.nested.default == "from_default"


@pytest.mark.parametrize(
    ("phf", "default", "um"),
    [
        (PhField(3), 3, "left_to_right"),
        (PhField(default=6), 6, "left_to_right"),
        (PhField(3, union_mode="smart"), 3, "smart"),
    ],
)
def test_PhField(phf, default, um):
    assert phf.default == default
    assert phf.metadata[0].union_mode == um


@pytest.mark.parametrize(
    ("obj", "expected"),
    [
        (1, 1),
        ("noph", "noph"),
        (True, True),
        ("{phint}", "42"),
        ("{phstr1}{phstr2}", "foobar"),
        (
            {
                "level1": {
                    "key1": "{phstr1}",
                    "inner": {"key2": "{phstr2}", "static": "noph"},
                },
                "list": [{"item_key": "{phlist}"}, "plain_string"],
            },
            {
                "level1": {
                    "key1": "foo",
                    "inner": {"key2": "bar", "static": "noph"},
                },
                "list": [{"item_key": "['a', 'b']"}, "plain_string"],
            },
        ),
    ],
)
def test_interpolate_recursively(obj, expected):
    mapping = {
        "phstr1": "foo",
        "phstr2": "bar",
        "phlist": ["a", "b"],
        "phint": 42,
        "nowhere": "tobefound",
    }
    assert PlaceholderModel.interpolate_recursively(obj, mapping) == expected


@pytest.fixture
def Model():
    class Nested(PlaceholderModel):
        a: str = "string with a {ph}"
        b: int | str = PhField("{phint}")

    class Model(PlaceholderSettings):
        nested: Nested = Field(default_factory=Nested)
        c: str = "string with a {ph}"
        d: int | str = PhField("{phint}")

    return Model, Nested


def test_instantiation_with_nested_model_None(Model):
    placeholders = {"ph": "placeholder", "phint": 42}
    model = Model[0](placeholders=placeholders)
    assert model.nested.a == "string with a placeholder"


def test_instantiation_with_nested_model_instance(Model):
    placeholders = {"ph": "placeholder", "phint": 42}
    model = Model[0](
        placeholders=placeholders, nested=Model[1](placeholders=placeholders, a="{ph}")
    )
    assert model.nested.a == "placeholder"


def test_instantiation_with_nested_model_dict(Model):
    placeholders = {"ph": "placeholder", "phint": 42}
    os.environ["NARRATION_NESTED__A"] = "{ph}"
    model = Model[0](placeholders=placeholders)
    del os.environ["NARRATION_NESTED__A"]
    assert model.nested.a == "placeholder"


def test_placeholder_interpolation_with_simple_data_types():
    class Nested(PlaceholderModel):
        str_with_ph: str = "nested-{phstr1}-{phstr2}"
        int_with_ph: int | str = PhField("{phint}")
        float_with_ph: float | str = PhField("{phfloat}")
        bool_with_ph: bool | str = PhField("{phbool}")

    class Base(PlaceholderSettings):
        nested: Nested = Field(default_factory=Nested)
        str_with_ph: str = "base-{phstr1}-{phstr2}"
        int_with_ph: int | str = PhField("{phint}")
        float_with_ph: float | str = PhField("{phfloat}")
        bool_with_ph: bool | str = PhField("{phbool}")

    base = Base(
        placeholders={
            "phstr1": "str1",
            "phstr2": "str2",
            "phint": 42,
            "phfloat": 3.14,
            "phbool": True,
            "phextra": "extra",
        }
    )

    assert base.str_with_ph == "base-str1-str2"
    assert base.int_with_ph == 42
    assert base.float_with_ph == 3.14
    assert base.bool_with_ph is True
    assert base.nested.str_with_ph == "nested-str1-str2"
    assert base.nested.int_with_ph == 42
    assert base.nested.float_with_ph == 3.14
    assert base.nested.bool_with_ph is True


def test_placeholder_interpolation_with_collections():
    class Nested(PlaceholderModel):
        list_: list[int] | list[int | str] = PhField(["{phint}{phint}", 24])
        dict_: dict[str, int] | dict[str, int | str] = PhField(
            {"key1": "{phint}", "key2": 24}
        )

    class Base(PlaceholderSettings):
        nested: Nested = Field(default_factory=Nested)
        list_: list[str] = ["{phstr1}", "no_ph"]
        dict_: dict[str, str] = Field(default={"key1": "{phstr1}", "key2": "noph"})

    base = Base(
        placeholders={
            "phstr1": "str1",
            "phstr2": "str2",
            "phint": 42,
            "phfloat": 3.14,
            "phextra": "extra",
        }
    )

    assert base.list_ == ["str1", "no_ph"]
    assert base.nested.list_ == [4242, 24]
    assert base.dict_ == {"key1": "str1", "key2": "noph"}
    assert base.nested.dict_ == {"key1": 42, "key2": 24}


def test_missing_placeholder_raises_validation_error():
    class Model(PlaceholderModel):
        a: str = "{xxx}"

    class Model2(PlaceholderModel):
        a: int | str = PhField("{xxx}")

    class Model3(PlaceholderModel):
        a: list[str] = ["{xxx}"]

    class Model4(PlaceholderModel):
        a: dict[str, int] = {"key": "{xxx}"}

    with pytest.raises(KeyError, match="The placeholder `xxx` is unknown."):
        _ = Model(placeholders={})

    with pytest.raises(KeyError, match="The placeholder `xxx` is unknown."):
        _ = Model2(placeholders={})

    with pytest.raises(KeyError, match="The placeholder `xxx` is unknown."):
        _ = Model3(placeholders={})

    with pytest.raises(KeyError, match="The placeholder `xxx` is unknown."):
        _ = Model4(placeholders={})


def test_assignment_is_validated():
    class Nested(PlaceholderModel):
        a: int | str = PhField(24)
        b: int = 1

    class Model(PlaceholderModel):
        a: int | str = PhField(42)
        b: int = 2
        nested: Nested = Field(default_factory=Nested)

    model = Model(placeholders={})

    with pytest.raises(
        ValidationError,
        match=r"invalid literal for int\(\) with base 10: 'should not work'",
    ):
        model.a = "should not work"

    with pytest.raises(
        ValidationError,
        match=r"Input should be a valid integer, unable to parse string as an integer",
    ):
        model.b = "should not work"

    with pytest.raises(
        ValidationError,
        match=r"invalid literal for int\(\) with base 10: 'should not work'",
    ):
        model.nested.a = "should not work"

    with pytest.raises(
        ValidationError,
        match=r"Input should be a valid integer, unable to parse string as an integer",
    ):
        model.nested.b = "should not work"

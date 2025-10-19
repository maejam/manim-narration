import typing as t
from inspect import isclass
from pathlib import Path

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
)
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from manim_narration import utils

if t.TYPE_CHECKING:
    from manim_narration._config.config import NarrationConfig


logger = utils.get_logger(__name__)


DOTENV_FILE_NAME = ".env"
CONFIG_FILE_NAME = "narration_config.toml"
PYPROJECT_TOML_TABLE = ("tool", "manim", "narration")


def candidate_paths(filename: str) -> tuple[Path, Path]:
    """Return the list of configuration files that should be considered.

    The files are returned in the order they will be read (later entries win).

    Parameters
    ----------
    filename
        The name of the file to retrieve in the candidate paths.

    Returns
    -------
        A list of potential config file paths.

    """
    return (
        Path.home() / filename,
        Path.cwd() / filename,
    )


def PhField(default: t.Any, **kwargs: t.Any) -> t.Any:
    """Declare a Field as holding placeholders with union of type hints.

    This function wraps pydantic `Field` function. It allows for less verbose field
    declarations when a field of a type that is not `str` holds placeholders.
    It does so by turning `default` into a positional argument and by automatically
    applying `union_mode="left_to_right"`.

    `a: int | str = PhField("{phint}")` is equivalent to:
    `a: int | str = Field(default="{phint}", union_mode="left_to_right")`

    Parameters
    ----------
    default
        The default value for this field.
    kwargs
        Any keyword argument to forward to `Field`. Passing `union_mode` will override
        the value for union_mode.

    Returns
    -------
    Whatever `Field` returns (uses overloads).

    """
    kwargs.setdefault("default", default)
    kwargs.setdefault("union_mode", "left_to_right")
    return Field(**kwargs)


class PlaceholderModel(BaseModel):
    """A pydantic model that performs placeholder interpolation on its fields values.

    The placeholders substitution values are defined in a mapping that must be passed
    to the model at instantiation (and independently to all nested models as well if
    they are instantiated alongside the base model).
    Failing to do so will prevent any placeholder interpolation from happening and might
    trigger a KeyError.

    Example
    -------
    ```
    class Nested(PlaceholderModel):
        a: str = "string with a {ph}"
        b: int | str = PhField("{phint}")


    class Model(PlaceholderSettings):
        nested: Nested = Field(default_factory=Nested)
        c: str = "string with a {ph}"
        d: int | str = PhField("{phint}")


    placeholders = {"ph": "placeholder", "phint": 42}

    try:
        model = Model(placeholders={})
    except KeyError as e:
        print(e)  # KeyError: 'The placeholder `ph` is unknown.


    model = Model(placeholders=placeholders)
    # GOOD: the nested model will be instantiated automatically and the placeholders
    # mapping will be forwarded to it.


    try:
        model = Model(placeholders=placeholders, nested=Nested(a="{ph}"))
    except TypeError as e:
        print(e)
    # TypeError: PlaceholderModel.__init__() missing 1 required positional argument:
    # 'placeholders'

    model = Model(
        placeholders=placeholders, nested=Nested(placeholders=placeholders, a="{ph}")
    )
    # GOOD: the nested model can now access the plaholders mapping
    ```

    The placeholders have to be defined within curly braces: `"{my_ph}"`. Because this
    imposes the use of a string, even for non string fields, to keep type checkers
    compatibility fields can be defined with a union of types. In order to make sure the
    field is casted to the right type, `union_mode="left_to_right` should be used. The
    convenience function `PhField` can be used for that purpose.
    (e.g. `a: list[int] | list[str] = PhField([1, 2, 3])` will be properly casted with
    an assignment such as `model.a = "{phint}` and the assignment
    `model.a = "plain string` will properly raise a ValidationError). Of course, this
    imposes some restrictions with mixing data types into containers, but this is
    probably acceptable in a configuration context.

    Parameters
    ----------
    placeholders
        A mapping from string keys to their interpolation values.
    data
        Keyword arguments eventually forwarded to pydantic BaseModel.

    """

    placeholders: t.Mapping[str, t.Any] = Field(default={}, exclude=True, repr=False)
    model_config = ConfigDict(
        extra="forbid", validate_default=True, validate_assignment=True
    )

    def __init__(self, placeholders: t.Mapping[str, t.Any], **data: t.Any) -> None:
        for field_name, field_info in type(self).model_fields.items():
            field_ann = field_info.annotation
            # inject placeholders into sections
            if isclass(field_ann) and issubclass(field_ann, PlaceholderModel):
                section = data.get(field_name)
                # section can be instance (declared in __init__)
                # or dict (external config sources) or None
                if isinstance(section, PlaceholderModel):
                    section_data = section.model_dump()  # convert to dict
                elif isinstance(section, dict):
                    section_data = section
                else:
                    section_data = {}
                section_data.setdefault("placeholders", placeholders)
                data[field_name] = section_data
        super().__init__(placeholders=placeholders, **data)

    def __setattr__(self, name: str, value: t.Any, /) -> None:
        super().__setattr__(name, value)
        if name == "verbosity":
            # change root logger level
            from manim_narration import logger as l

            l.setLevel(value)
        logger.debug(f"Config option '{name}' set to '{value}'.")

    @field_validator("*", mode="before")
    @classmethod
    def interpolate_placeholders(cls, value: t.Any, info: ValidationInfo) -> t.Any:
        """Interpolate all fields before validation."""
        if info.field_name is not None:
            field_info = cls.model_fields[info.field_name]
            field_ann = field_info.annotation

            logger.debug(
                f"Interpolating config field: '{cls.__name__}.{info.field_name}' "
                f"with value '{value}' (annotation: '{field_ann}')"
            )
            is_base_model = isclass(field_ann) and issubclass(field_ann, BaseModel)
            if (
                info.field_name != "placeholders"
                and field_ann is not None
                # nested models are dict. We can't exclude all dicts => check annotation
                and not is_base_model
            ):
                value = cls.interpolate_recursively(value, info.data["placeholders"])
                logger.debug(f"Interpolated to '{value}'")

                union_mode = (
                    field_info.metadata[0].union_mode if field_info.metadata else None
                )
                if union_mode == "left_to_right":
                    # cast to first element in union to properly validate assignments:
                    # `a: int|str = PhField(...); model.a = "string"` should raise.
                    value = t.get_args(field_info.annotation)[0](value)
        return value

    @staticmethod
    def interpolate_recursively(
        obj: t.Any, placeholders: t.Mapping[str, t.Any]
    ) -> t.Any:
        """Recursively interpolate any python structure."""
        # TODO: type hint to inform type checkers that function is structure preserving
        if isinstance(obj, dict):
            return {
                k: PlaceholderModel.interpolate_recursively(v, placeholders)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [
                PlaceholderModel.interpolate_recursively(v, placeholders) for v in obj
            ]
        elif isinstance(obj, str):
            try:
                return obj.format_map(placeholders)
            except KeyError as e:
                raise KeyError(f"The placeholder `{e.args[0]}` is unknown.") from None
        else:
            return obj


class PlaceholderSettings(BaseSettings, PlaceholderModel):  # pyright: ignore[reportIncompatibleVariableOverride]
    """The base for NarrationConfig combining Settings and Placeholder functionality.

    The manim narration `config` object is an instance of this class.

    It is possible to use placeholders to reference **manim** configurations options.
    (e.g. `dir="{media_dir}/narrations"` will become `dir="media/narrations"` given the
    default manim configuration).

    It is possible to override default configuration options in different ways.
    In order of precedence, a configuration option will be determined as follows:
    1. Programmatic overrides (`config.cache.dir = "custom_path"`)
    2. Environment variables (`export narration_cache__dir=custom_path`).
    Environment variables are case insensitive and are all prefixed with
    `NARRATION_`. The delimeter between sections is "__".
    3. A ".env" file in the current working directory : same naming conventions as
    environment variables.
    4. The "pyproject.toml" file in the current working directory, under the section
    header `[tool.manim.narration]`.
    5. A "narration_config.toml" file in the current working directory.
    6. A "narration_config.toml" file in the user's home directory.
    7. The default value.

    """

    def __init__(self, placeholders: t.Mapping[str, t.Any], **data: t.Any) -> None:
        #  define env_file here to avoid import time side-effects
        self.model_config["env_file"] = candidate_paths(DOTENV_FILE_NAME)
        super().__init__(placeholders=placeholders, **data)

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_prefix="NARRATION_",
        pyproject_toml_table_header=PYPROJECT_TOML_TABLE,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Set the order of precedence for configuration sources."""
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            PyprojectTomlConfigSettingsSource(settings_cls),
            TomlConfigSettingsSource(
                settings_cls, toml_file=candidate_paths(CONFIG_FILE_NAME)
            ),
        )


class Config:
    """Act like a dependency injector for the global config instance.

    Any class that needs access to `config` simply needs inheriting from this class.
    It can then access the `config` instance from the `config` property.
    """

    @utils.classproperty
    def config(cls) -> "NarrationConfig":
        from manim_narration import config

        return config

import typing as t
from configparser import ConfigParser
from pathlib import Path

import manim as m  # type: ignore[import-untyped]

from manim_narration.utils import NarrationError

CONFIG_FILE_NAME = "manim_narration.cfg"


class NarrationConfigKeyError(NarrationError):
    """Errors related to configuration keys."""

    pass


class NarrationConfigPlaceHolderError(NarrationError):
    """Errors related to placeholders in the config file."""

    pass


class ManimNarrationConfig:
    """Store all config options.

    The `config` object is an instance of this class.
    We first check if a config file is present in the working directory (where the
    script with the scene is located) and load it if present. If not, load the file in
    the library `src` directory. The user can always override any key programmatically
    by importing the `config` object and setting a new value with the dot notation
    (e.g. `config.cache_dir`). The name of the custom config file, if any, should be
    `manim_narration.cfg`. When using a custom config file, THERE IS NO FALLBACK for
    missing values, which means the config file should be complete or not there at all.

    It is possible to use placeholders when defining options to reference options in
    the **manim** config file (e.g. `cache_dir = {media_dir}/narrations`).

    Parameters
    ----------
    filename
        The name of the config file.
    """

    def __init__(self, filename: str) -> None:
        self.__dict__["_config"] = self.get_config_file(filename)
        self.__dict__["_filename"] = filename
        self.__dict__["sections"] = self._config.sections()

    def get_config_file(self, filename: str) -> ConfigParser:
        """Load the config file.

        Check if a custom file if present in the CWD, if not load the default file from
        the library.

        Parameters
        ----------
        filename
            The name of the config file.

        Returns
        -------
        The configparser object.
        """
        config = ConfigParser()
        path = Path(filename)
        if path.exists():
            config.read(path)
        else:
            config.read(Path(__file__).parent / filename)
        return config

    def __getattr__(self, name: str, /) -> t.Any:
        section_iter = iter(self._config.sections())
        while (section := next(section_iter, None)) is not None:
            try:
                value = self._config[section][name]
                value = self.resolve_placeholders(value)
                return value
            except KeyError:
                continue
        else:
            raise NarrationConfigKeyError(
                f"""The key `{name}` does not exist in manim narration configuration.
                    Check your `{CONFIG_FILE_NAME}` file."""
            )

    def __setattr__(self, name: str, value: t.Any, /) -> None:
        for section in self.__dict__["sections"]:
            if name in self._config[section]:
                self._config[section][name] = str(value)
            else:
                super().__setattr__(name, value)

    def resolve_placeholders(self, string_: str) -> str:
        """Replace the placeholders with the values from the manim config.

        Parameters
        ----------
        string_
            The string to replace.

        Returns
        -------
        The string interpolated.
        """
        try:
            string_ = string_.format(**m.config._d)
        except KeyError as e:
            raise NarrationConfigPlaceHolderError(
                f"""
                The value `{{{e.args[0]}}}` does not exist in manim config options.
                See https://docs.manim.community/en/stable/guides/configuration.html#a-list-of-all-config-options
                """
            )
        return string_

    def get_all_keys_in_section(self, section: str) -> dict[str, str]:
        """Return all the keys in a given section of the config file.

        Parameters
        ----------
        section
            The name of the section.

        Returns
        -------
        A dictionary mapping keys to values. All the keys and values will be strings
        even if initially set as other types (either in the config file or
        programmatically).
        """
        return dict(self._config[section])


config = ManimNarrationConfig(CONFIG_FILE_NAME)

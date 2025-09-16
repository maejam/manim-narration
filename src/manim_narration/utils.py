import json
import re
import typing as t
from pathlib import Path


class NarrationError(Exception):
    """The base class for all exceptions in this library."""

    pass


def remove_tags(text: str) -> str:
    """Remove the tags from a given string.

    Parameters
    ----------
    text
        The text to process.

    Returns
    -------
    The text without the tags.
    """
    return re.sub(r"<.*?/>", "", text)


def append_to_json_file(json_file: Path, data: t.Any) -> None:
    """Add data at the end of a json file.

    The data will only be added if it is not already in the file.

    Parameters
    ----------
    json_file
        The file to append to.
    data
        The data to append to the file.
    """
    if not json_file.exists():
        with json_file.open("w") as jf:
            json.dump([data], jf, indent=2)
    else:
        with json_file.open("r") as jf:
            json_data = json.load(jf)
        if data not in json_data:
            json_data.append(data)
            with json_file.open("w") as jf:
                json.dump(json_data, jf, indent=2)

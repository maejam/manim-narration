import hashlib
import json
import re
import typing as t

# from pathlib import Path
import manim_narration.config_ as config_


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
    tags = list(config_.config.get_all_keys_in_section("TAGS").values())
    tags_group = f"{'|'.join(tag for tag in tags)}"
    pattern = f"<({tags_group}) .*?/>"
    return re.sub(pattern, "", text)


def get_hash_from_data(data: t.Any, hash_algo: str, hash_len: int = -1) -> str:
    """Compute the hash of any json-serializable object.

    For now this function is only implemented for dictionaries. Implementations for
    other data types will be added if necessary.

    data
        The data to hash.
    hash_algo
        The hash algorithm to use. See https://docs.python.org/3/library/hashlib.html.
    hash_len
        If positive, the computed hash will be truncated to the given length.
        If zero or negative (the default), the full computed hash is returned.

    Returns
    -------
    The computed hash.

    Raises
    ------
    NotImplementedError
        If given anything else than a dictionary.
    """
    if isinstance(data, dict):
        raw_data = json.dumps(
            # sort_keys to ensure stable order, separators for compactness
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
    else:
        raise NotImplementedError

    h = hashlib.new(hash_algo)
    h.update(raw_data)
    digest = h.hexdigest()
    if hash_len > 0:
        digest = digest[:hash_len]

    return digest


# def append_to_json_file(json_file: Path, data: t.Any) -> None:
#     """Add data at the end of a json file.
#
#     The data will only be added if it is not already in the file.
#
#     Parameters
#     ----------
#     json_file
#         The file to append to.
#     data
#         The data to append to the file.
#     """
#     if not json_file.exists():
#         with json_file.open("w") as jf:
#             json.dump([data], jf, indent=2)
#     else:
#         with json_file.open("r") as jf:
#             json_data = json.load(jf)
#         if data not in json_data:
#             json_data.append(data)
#             with json_file.open("w") as jf:
#                 json.dump(json_data, jf, indent=2)

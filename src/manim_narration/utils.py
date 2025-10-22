import hashlib
import json
import logging
import re
import typing as t
from collections.abc import Mapping


class NarrationError(Exception):
    """The base class for all exceptions in this library."""

    pass


def get_logger(name: str) -> logging.Logger:
    """Ensure the loggers are in the manim logger hierarchy."""
    return logging.getLogger(f"manim.{name}")


# T = t.TypeVar("T")
R = t.TypeVar("R")


class classproperty(t.Generic[R]):
    """classmethod properties are deprecated since 3.11 and removed in 3.13."""

    # TODO: find how to annotate properly
    def __init__(self, func: t.Callable[[t.Any], R]) -> None:
        self._func = func

    def __get__(self, _: t.Any, owner: t.Any) -> R:
        return self._func(owner)


def get_hash_from_data(data: t.Any, hash_algo: str, hash_len: int) -> str:
    """Compute the hash of a json-serializable object.

    For now this function is only implemented for mappings. Implementations for
    other data types will be added if necessary.

    data
        The data to hash.
    hash_algo
        The hash algorithm to use. See https://docs.python.org/3/library/hashlib.html.
    hash_len
        If positive, the computed hash will be truncated to the given length.
        If zero or negative, the full computed hash is returned.

    Returns
    -------
    The computed hash.

    Raises
    ------
    NotImplementedError
        If given anything else than a mapping.

    """
    if isinstance(data, Mapping):
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


def split_after_characters(text: str, chars: str) -> list[str]:
    """Split a text after a predefined set of characters.

    Parameters
    ----------
    text
        The text to split.
    chars
        The set of individual characters to split on. If multiple consecutive
        characters are found, they will be treated as one. For example, the text
        `"Hello, world!!!"` will return `["Hello,", "world!!!"]` with
        `chars = ",!"`.

    """
    # split on chars with look-behind pattern to keep the chars with their split
    if chars:
        pattern = rf"(?<=[{re.escape(chars)}])\s+"
        splits = re.split(pattern, text)
    else:
        splits = [text]
    return splits


def regroup_splits(splits: list[str], max_len: int) -> list[str]:
    """Regroup strings in a list without exceeding a maximum length.

    Parameters
    ----------
    splits
        A list of strings.
    max_len
        The maximum length that strings in the new list should never exceed.

    Returns
    -------
    A list of strings where each element in the original list is regrouped with the
    previous one iff their combined length is not exceeding `max_len`.

    """
    regrouped = []  # will hold splits after grouping
    group = ""  # will hold the current group being processed

    for split in splits:
        if not split:
            continue
        if len(split) > max_len:
            if group:
                regrouped.append(group)
                group = ""
            regrouped.append(split)
            continue
        if len(group) + len(split) <= max_len - 1:  # account for space
            group = f"{group} {split}" if group else split
        else:
            regrouped.append(group)
            group = split
    if group:
        regrouped.append(group)
    return regrouped

import hashlib
import json
import typing as t
from collections.abc import Mapping


class NarrationError(Exception):
    """The base class for all exceptions in this library."""

    pass


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

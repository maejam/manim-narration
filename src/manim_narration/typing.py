import typing as t

T = t.TypeVar("T")


class SpeechData(t.TypedDict):
    """Uniquely identify a speech generation.

    When a speech is generated, it is saved in cache under a directory named after the
    hash of this data. It is therefore essential for the included data to be able to
    identify a given speech generation precisely and uniquely.
    """

    input_text: str
    service_name: str
    service_kwargs: dict[str, t.Any]


@t.overload
def all_strings(sequence: list[T]) -> t.TypeGuard[list[str]]: ...
@t.overload
def all_strings(sequence: tuple[T, ...]) -> t.TypeGuard[tuple[str]]: ...
def all_strings(sequence: t.Iterable[T]) -> bool:
    """Return True iff every element is a string."""
    return all(isinstance(item, str) for item in sequence)

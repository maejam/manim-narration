import typing as t


class SpeechData(t.TypedDict):
    """Uniquely identify a speech generation.

    When a speech is generated, it is saved in cache under a directory named after the
    hash of this data. It is therefore essential for the included data to be able to
    identify a given speech generation precisely and uniquely.
    """

    input_text: str
    service_name: str
    service_kwargs: dict[str, t.Any]

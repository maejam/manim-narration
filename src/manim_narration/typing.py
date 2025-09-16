import typing as t


class InputData(t.TypedDict):
    """Sub dict in SpeechData."""

    input_text: str
    service: str


class SpeechData(t.TypedDict):
    """The format for speech services return values."""

    input_text: str
    input_data: InputData
    original_audio: str
    final_audio: str

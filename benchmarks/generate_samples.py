from pathlib import Path

from manim_narration.speech import (
    ChatterboxService,
    CoquiService,
    GTTSService,
    KokoroService,
)

PATH = Path(__file__).parent / "narrations/"
SPEECH_SERVICES = [
    CoquiService(
        "tts_models/multilingual/multi-dataset/xtts_v2",
        language="en",
        speaker="Claribel Dervla",
    ),
    GTTSService(),
    KokoroService(),
    ChatterboxService(language_id="en"),
]
TEXT = (
    "Narration is the use of a written or spoken commentary "
    "to convey a story to an audience."
)
PATH.mkdir(parents=True, exist_ok=True)

for service in SPEECH_SERVICES:
    service_name = type(service).__name__[:-7]
    print(
        f"\n=============== Generating sample audio file: {service_name}"
        " ==============="
    )
    audio_file_path = PATH / f"{service_name}.wav"

    res = service.generate_speech(text=TEXT, audio_file_path=audio_file_path)
    print(f"File saved: {audio_file_path}")

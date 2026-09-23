"""
Alignment is the process of determining when a word in a audio file is being spoken.
This allows two things in manim-narration:
1. The use of bookmarks to synchronise the animation with the narration.
2. The synchronisation of subtitles with the narration.

As of v1.2, three sevices are available:
1. ManualAligner: aligns every bookmark to the very begining of the speech,
essentially doing nothing and letting the user manually adjust timings.
2. InterpolationAligner: this is the default aligner and it is automatically
instantiated with every scene because it is very lightweight and gives decent
results, especially for short narrations. It simply interpolates the timestamp
from the position of the desired character in the original text and the duration of
the audio file (timestamp = audio_duration * char_offset / len(text)).
3. CTCAligner: uses machine learning models to perform the alignment.
It is more accurate but also requires much more resources.

Once generated, alignments, just like speeches, are cached.
They will be re-calculated only if the text or the service parameters are changed.
"""

from manim import *

from manim_narration import NarrationScene
from manim_narration.alignment import CTCAligner, InterpolationAligner, ManualAligner
from manim_narration.speech import GTTSService


class GettingStarted(NarrationScene):
    def construct(self) -> None:
        self.set_speech_services(en=GTTSService(lang="en"))

        # Set alignment services
        # Would otherwise default to: {"default": InterpolationAligner()}
        self.set_alignment_services(
            manual=ManualAligner(),
            interpolator=InterpolationAligner(),
            ctc=CTCAligner(language="en"),
        )

        # Both speech and alignment services default to the first ones defined
        # in the methods above. Here `ggts` and `manual`.
        with self.narration(
            text="With manual alignment <bookmark mark='users'/>users "
            "must adjust the timings themselves",
        ) as narration:
            # The `offset` is realtive to the begining of the narration
            self.wait_until_bookmark("users", offset=1.6)
            txt = Text("Users")
            self.add(txt)
            self.wait_for_narration_to_finish()
            self.remove(txt)
        self.wait()

        with self.narration(
            "en",  # speech service
            "interpolator",  # alignement service
            text="Interpolation alignment will align very "
            "<bookmark mark='roughly'/>roughly. "
            "It is always possible to adjust with the offset parameter.",
        ) as narration:
            self.wait_until_bookmark("roughly", offset=-0.1)  # can be negative
            txt = Text("Roughly")
            self.add(txt)
            self.wait_for_narration_to_finish()
            self.remove(txt)
        self.wait()

        with self.narration(
            "en",
            "ctc",
            text="CTC alignment will be much more precise, especially on a longer "
            "narration, but will also take longer. "
            "Lorem Ipsum is simply dummy text of the printing and typesetting "
            "industry. Lorem Ipsum has been the industry's standard dummy text "
            "ever since <bookmark mark='1966'/>1966, when designers at Letraset "
            "and James Mosley, the librarian at St Bride Printing Library in "
            "<bookmark mark='London'/>London, took a 1914 Cicero "
            "translation and scrambled it to make dummy text for Letraset's "
            "Body Type sheets.",
        ) as narration:
            self.wait_until_bookmark("1966", offset=-1.5)
            date = Text("1966")
            self.play(
                date.animate.shift(RIGHT * 3),
                run_time=narration.duration_until_bookmark("London") + 1.5,
            )
            city = Text("London").move_to(date)
            self.play(ReplacementTransform(date, city), run_time=0.1)
            self.play(
                city.animate.shift(LEFT * 3), run_time=narration.remaining_duration
            )
            self.remove(city)

        # Subcaptions can be aligned idependently, allowing the use of another service.
        # Manual alignment does not make sense here.
        with self.narration(
            "en",  # speech service
            "interpolator",  # bookmarks alignment service
            text="Subcaptions should be aligned with the speech. See the in-code "
            "documentation for more options to control how subcaptions are split.",
            create_subcaption=True,
            subcaption_aligner_id="ctc",  # subcaption alignment service
        ):
            self.wait_for_narration_to_finish()

import manim as m

from manim_narration import NarrationScene
from manim_narration.alignment import InterpolationAligner
from manim_narration.speech import GTTSService


class GettingStarted(NarrationScene):
    def construct(self) -> None:
        # define speech services with a name
        self.set_speech_services(en=GTTSService(lang="en"), fr=GTTSService(lang="fr"))
        # optionally set an alignment service (ManualAlignment is the default)
        self.set_alignment_service(InterpolationAligner())

        en = m.Text(
            "Narration is the use of a written or spoken\n commentary to convey a "
            "story to an audience.",
            font_size=30,
        )
        comm = m.Text("commentaire", font_size=30).next_to(en, m.DOWN)
        hist = m.Text("histoire", font_size=30).next_to(comm, m.RIGHT)

        # the first argument is the speech service to use.
        # if it is not set, the first one will be used.
        with self.narration(text=en.text) as narration:
            self.play(m.Write(en), run_time=narration.duration)
        with self.narration(
            "fr",
            text="Une narration consiste a utiliser un <bookmark mark='comm'/>"
            "commentaire écrit ou parlé afin de transmettre une "
            "<bookmark mark='hist'/>histoire à un public.",
        ) as narration:
            # adjust the timing with `offset` and adding to `run_time` if needed
            self.wait_until_bookmark("comm", offset=-0.5)
            self.play(
                m.Write(comm), run_time=narration.duration_until_bookmark("hist") - 0.5
            )
            self.play(m.Write(hist), run_time=narration.remaining_duration)

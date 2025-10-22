import manim as m

from manim_narration import NarrationScene
from manim_narration.alignment import CTCAligner, InterpolationAligner
from manim_narration.speech import GTTSService


class GettingStarted(NarrationScene):
    def construct(self) -> None:
        # define speech services with a name
        self.set_speech_services(
            en=GTTSService(lang="en"),
            fr=GTTSService(lang="fr"),
        )
        # optionally set alignment services
        # would default to: {"default": InterpolationAligner()}
        self.set_alignment_services(
            bookmarks=InterpolationAligner(),
            subcaptions=CTCAligner(language="fr"),
        )

        en_txt = (
            "Narration is the use of a written or spoken \n"
            "commentary to convey a story to an audience."
        )

        en = m.Text(en_txt, font_size=30)
        comm = m.Text("commentaire", font_size=30).next_to(en, m.DOWN)
        hist = m.Text("histoire", font_size=30).next_to(comm, m.RIGHT)

        # the first argument to the context manager is the speech service to use.
        # (defaults to the first in set_speech_services)
        # the second argument is the aligner to use for bookmarks
        # (defaults to the first in set_alignment_services)
        # Using default services is very concise, just like voiceover...
        with self.narration(text=en_txt) as narration:
            self.play(m.Write(en), run_time=narration.duration)
        # ...but customization is possible (see the doc for more subcaption options)
        with self.narration(
            "fr",  # speech service to be used
            "bookmarks",  # aligner to be used for bookmarks
            text="Une narration consiste a utiliser un <bookmark mark='comm'/>"
            "commentaire écrit ou parlé afin de transmettre une "
            "<bookmark mark='hist'/>histoire à un public.",
            create_subcaption=True,
            subcaption_aligner_id="subcaptions",  # aligner to be used for subcaptions
        ) as narration:
            # adjust the timing with `offset` and adding to `run_time` if needed
            # here we use InterpolationAligner for bookmarks, so it is likely needed
            self.wait_until_bookmark("comm", offset=-1.5)
            self.play(
                m.FadeIn(comm), run_time=narration.duration_until_bookmark("hist") - 0.5
            )
            self.play(m.FadeIn(hist), run_time=narration.remaining_duration)

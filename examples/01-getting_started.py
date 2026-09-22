from manim import *

from manim_narration import NarrationScene
from manim_narration.speech import GTTSService


class GettingStarted(NarrationScene):
    def construct(self) -> None:
        # define speech service(s) with a name
        self.set_speech_services(
            en=GTTSService(lang="en"),
            fr=GTTSService(lang="fr"),
        )

        en_txt = (
            "Narration is the use of a written or spoken \n"
            "commentary to convey a story to an audience."
        )
        fr_txt = (
            "Une narration consiste a utiliser un commentaire écrit ou parlé \n"
            "afin de transmettre une histoire à un public."
        )

        # The first argument to the context manager is the speech service to use.
        # If ommited, it will default to the first one defined in set_speech_services.
        with self.narration(text=en_txt) as narration:
            self.play(
                FadeIn(Text(en_txt, font_size=30).shift(UP)),
                run_time=narration.duration,
            )

        # To use any other speech service, pass its name as the first argument.
        with self.narration(
            "fr",
            text=fr_txt,
            create_subcaption=True,
        ) as narration:
            self.play(
                Write(Text(fr_txt, font_size=30).shift(DOWN)),
                run_time=narration.duration,
            )

"""
Unlike manim-voiceover, narration generation and playback are decoupled. This means you
can generate them all first and play them later.

manim-narration provides 2 methods to generate narrations:
1. `NarrationScene.generate_narration` will generate exactly one narration.
2. `NarrationScene.generate_narrations` will generate multiple narrations at once,
using one of 3 modes: "sequential", "multithreading" or "multiprocessing". This allows
to generate narrations much faster and to declutter your scenes. Note that as of v1.2,
multiprocessing is unstable and strongly discouraged.

Narrations can be played in 2 ways:
1. Using the usual context manager (`with self.narration(...)`). Passing a `text`
argument will generate the narration from the text and play it instantly. Passing a
tracker object (as returned by the methods above) to the `narration` parameter
will simply play the related narration.
2. `NarrationScene.add_narration`: works in pretty much the same way but as a regular
method (not a context manager).
"""

from manim_narration import NarrationScene
from manim_narration.speech import GTTSService


class GettingStarted(NarrationScene):
    def setup(self) -> None:
        """The setup method seems like a good place to generate narrations beforehand."""
        self.set_speech_services(en=GTTSService(lang="en"))

        # Generate a single narration and store in variable.
        self.hello = self.generate_narration(text="Hello there!")

        # Generate multiple narrations using multithreading.
        # Returns a dictionary with each task name as the key and the resulting
        # tracker object as the value.
        # Depending on the speech service used and your machine, you may encounter
        # issues with multithreading. If so, limit the number of simultaneaous workers
        # with the `max_worker` parameter.
        self.narrations = self.generate_narrations(
            one="Narration number one",
            two="Narration number two",
            three="Narration number three",
        )

    def construct(self) -> None:
        # play using context manager
        with self.narration(narration=self.hello) as narration:
            print(narration)
            # NarrationTracker(text="Hello there!")

        # play using regular method - the only difference is that the context manager
        # automatically waits for the end of the narration before moving on.
        # `add_narration` does not: this can be useful in some circumstances.
        narration = self.add_narration(narration=self.narrations["one"])
        print(narration)
        # NarrationTracker(text="Narration number one")

        self.wait_for_narration_to_finish()

        narration = self.add_narration(narration=self.narrations["two"])
        print(narration)
        # NarrationTracker(text="Narration number two")

        narration = self.add_narration(narration=self.narrations["three"])
        print(narration)
        # NarrationTracker(text="Narration number three")

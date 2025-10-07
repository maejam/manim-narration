import textwrap
import typing as t
from contextlib import contextmanager
from pathlib import Path

import manim as m

from manim_narration import tags, utils
from manim_narration._config.base import Config
from manim_narration.speech.base import SpeechService
from manim_narration.tracker import NarrationTracker


class NarrationScene(m.Scene, Config):  # type: ignore[misc]
    """Add narration to a scene."""

    def set_speech_services(
        self,
        create_subcaption: bool = False,
        **speech_services: SpeechService,
    ) -> None:
        """Set the services used to generate speech.

        This method should be called before adding any narration to the scene.

        Parameters
        ----------
        create_subcaption
            Whether to create subcaptions for the scene. This is a global parameter
            that will be passed to all the `speech_services`.
        speech_services
            The speech services to be used. See their respective documentations for
            a list of all possible parameters. All the parameters above can also be
            set for each service individually.

        """
        self.speech_services = speech_services
        self.create_subcaption = (
            # don't create subcaptions if -s
            False if m.config.save_last_frame else create_subcaption
        )
        if self.create_subcaption:
            for service in self.speech_services.values():
                service.create_subcaption = True

        self.cache_dir = Path(self.config.cache.dir)
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)

    @contextmanager
    def narration(
        self, service_id: str | None = None, **kwargs: t.Any
    ) -> t.Generator[NarrationTracker, t.Any, None]:  # last 2 parameters for 3.10 only
        """Add narration to a scene through a context manager.

        Parameters
        ----------
        service_id
            The identifier of the service to be used. Defaults to the first service
            declared in `set_speech_services`.

        kwargs
            Other parameters passed to `add_narration`.

        Yields
        ------
            The NarrationTracker object.

        """
        yield self.add_narration(service_id, **kwargs)
        self.wait_for_narration_to_finish()

    def add_narration(
        self,
        service_id: str | None = None,
        *,
        text: str = "",
        subcaption: str = "",
        **subcaption_kwargs: t.Any,
    ) -> NarrationTracker:
        """Add narration to the scene.

        Parameters
        ----------
        service_id
            The identifier of the service to be used. Defaults to the first service
            declared in `set_speech_services`.
        text
            The text to be spoken.
        subcaption
            Alternative subcaption text. Defaults to `text`.
        subcaption_kwargs
            Other keyword arguments passed to `add_sucaption_text`.

        Returns
        -------
        The tracker object for this narration.

        """
        # get service
        service_id = service_id or next(iter(self.speech_services))
        service = self.speech_services[service_id]

        # clean up text
        parser = tags.TagParser(tags_to_consider=self.config.tags.all_tags)
        parser.feed(text)
        clean_text = parser.text
        # remove newlines and multiple consecutive spaces
        clean_text = " ".join(text.split())

        # call service
        audio_file_path = service._get_speech(clean_text)
        self.tracker = NarrationTracker(
            current_time=self.time, audio_file_path=audio_file_path
        )
        self.add_sound(str(audio_file_path))

        if service.create_subcaption:
            # clean remaining tags from text (e.g. ssml tags)
            parser = tags.TagParser()
            parser.feed(text)
            clean_text = parser.text

            subcaption = subcaption or clean_text

            self.add_subcaption_text(
                subcaption,
                self.tracker.duration,
                **subcaption_kwargs,
            )

        return self.tracker

    def add_subcaption_text(
        self,
        text: str,
        duration: float,
        max_subcaption_len: int = 70,
        subcaption_buff: float = 0.3,
        prefer_splitting_after_chars: str = ".!?,;:",
    ) -> None:
        """Add a subcaption to the scene.

        Parameters
        ----------
        text
            The text to be displayed as subcaption.
        duration
            The duration of the subcaption in seconds.
        max_subcaption_len
            Maximum number of characters for a subcaption. Subcaptions that are longer
            are split into smaller chunks.
        subcaption_buff
            The duration between split subcaption chunks in seconds.
        prefer_splitting_after_chars
            A list of characters to split after. Defaults to punctuation marks
            (`".!?,;:"`).

        """
        if prefer_splitting_after_chars:
            splits = utils.split_after_characters(text, prefer_splitting_after_chars)
            # regroup when possible without exceeding max_subcaption_len
            regrouped = utils.regroup_splits(splits, max_subcaption_len)
        else:
            regrouped = [text]

        # wrap to make sure nothing exceeds max_subcaption_len
        wraps_list = [
            textwrap.wrap(group, width=max_subcaption_len) for group in regrouped
        ]
        offset = 0.0
        for wrap in wraps_list:
            for chunk in wrap:
                chunk_duration = (len(chunk) / len(text)) * duration
                self.add_subcaption(
                    chunk,
                    duration=chunk_duration - subcaption_buff,
                    offset=offset,
                )
                offset += chunk_duration

    def wait_for_narration_to_finish(self) -> None:
        """Wait until the end of the current narration.

        The minimal waiting duration is one frame.

        """
        duration = (
            self.tracker.get_remaining_duration(self.time) + 1 / m.config["frame_rate"]
        )
        self.wait(duration)

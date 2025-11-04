import itertools
import textwrap
import typing as t
from contextlib import contextmanager
from pathlib import Path

import manim as m

from manim_narration import tags, utils
from manim_narration._config.config_base import Config
from manim_narration.alignment import InterpolationAligner, ManualAligner
from manim_narration.alignment.aligner_base import AlignmentError, AlignmentService
from manim_narration.speech.speech_base import SpeechService, SpeechServiceError
from manim_narration.tracker import NarrationTracker
from manim_narration.typing import AlignmentData

logger = utils.get_logger(__name__)


class NarrationScene(m.Scene, Config):  # type: ignore[misc]
    """Add narration to a scene.

    Attributes
    ----------
    speech_services
        A dictionary mapping speech service identifiers to instances.
        It must be set by the user before adding any narration to the scene by calling
        `NarrationScene.set_speech_services`.
    alignment_services
        A dictionary mapping alignment service identifiers to instances.
        It can be set by the user before adding bookmarks and subcaption to narrations
        by calling `NarrationScene.set_alignment_services`. If this method is not
        called, an InterpolationAligner instance will be used as the default aligner.

    """

    def __init__(self, **kwargs: t.Any) -> None:
        super().__init__(**kwargs)
        self.cache_dir = Path(self.config.cache.dir)
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.speech_services: dict[str, SpeechService] = {}
        self.alignment_services: dict[str, AlignmentService] = {
            "default": InterpolationAligner()
        }

    def render(self, preview: bool = False) -> None:
        try:
            super().render(preview)
        except ValueError as e:
            if "0 seconds which Manim cannot render." in str(e):
                message = "An error occured.\n"
                if isinstance(self.tracker.alignment_service, ManualAligner):
                    message += "Did you forget to manually align your bookmarks?\n"
                message += "Your bookmarks alignment might be inconsistent: "
                message += str(self.tracker.bookmark_timestamps)
                raise AlignmentError(message) from e
            raise e

    def set_speech_services(
        self,
        **speech_services: SpeechService,
    ) -> None:
        """Set the services used to generate speech.

        This method should be called before adding any narration to the scene.

        Parameters
        ----------
        speech_services
            The speech services to be used. See their respective documentations for
            a list of all possible parameters.

        """
        self.speech_services = speech_services

    def set_alignment_services(self, **alignment_services: AlignmentService) -> None:
        """Set the services used to align text and speech.

        Parameters
        ----------
        alignment_services
            The alignment services to be used. See their respective documentations for
            a list of all possible parameters.
            Defaults to `{"default": InterpolationAligner()}`.

        """
        self.alignment_services = alignment_services

    @contextmanager
    def narration(
        self,
        speech_service_id: str | None = None,
        alignment_service_id: str | None = None,
        **kwargs: t.Any,
    ) -> t.Generator[NarrationTracker, t.Any, None]:
        """Add narration to a scene through a context manager.

        Parameters
        ----------
        speech_service_id
            The identifier of the service to be used. Defaults to the first service
            declared in `set_speech_services`.
        alignment_service_id
            The identifier of the alignment service to be used. Defaults to the first
            service declared in `set_alignment_services` (which is
            `InterpolationAligner()` if `set_alignment_services` was never called).
        kwargs
            Other parameters passed to `add_narration`.

        Yields
        ------
            The NarrationTracker object.

        """
        yield self.add_narration(speech_service_id, alignment_service_id, **kwargs)
        self.wait_for_narration_to_finish()

    def add_narration(
        self,
        speech_service_id: str | None = None,
        alignment_service_id: str | None = None,
        *,
        text: str = "",
        create_subcaption: bool = False,
        subcaption: str = "",
        **subcaption_kwargs: t.Any,
    ) -> NarrationTracker:
        """Add narration to the scene.

        Parameters
        ----------
        speech_service_id
            The identifier of the speech service to be used. Defaults to the first
            service declared in `set_speech_services`.
        alignment_service_id
            The identifier of the alignment service to be used. Defaults to the first
            service declared in `set_alignment_services` (which is
            `InterpolationAligner()` if `set_alignment_services` was never called).
        text
            The text to be spoken.
        create_subcaption
            Whether to create subcaptions for this narration or not.
        subcaption
            Alternative subcaption text. Defaults to `text`.
        subcaption_kwargs
            Other keyword arguments passed to `add_sucaption_text`.

        Returns
        -------
        The tracker object for this narration.

        """
        if not self.config.render_narrations:
            # return a Tracker object so that everything still works without actually
            # generating the speech and computing an expensive alignment.
            # Since alignments are cached in `audio_file_path.parent`, these will be
            # cached in `config.cache.dir`.
            audio_file_path = Path(self.config.cache.dir) / "unrendered.wav"
            self.tracker = NarrationTracker(
                self,
                start_time=self.time,
                alignment_service=InterpolationAligner(),
                raw_text=text,
                audio_file_path=audio_file_path,
            )
            return self.tracker

        # get services
        speech_service = self._get_speech_service_from_id(speech_service_id)
        alignment_service = self._get_alignment_service_from_id(alignment_service_id)

        # clean up text
        parser = tags.TagParser(tags_to_remove=self.config.tags.all_tags)
        parser.feed(text)
        clean_text = parser.text
        # remove newlines and multiple consecutive spaces
        clean_text = " ".join(clean_text.split())

        # call service
        audio_file_path = speech_service._get_speech(clean_text)
        self.tracker = NarrationTracker(
            self,
            start_time=self.time,
            alignment_service=alignment_service,
            raw_text=text,
            audio_file_path=audio_file_path,
        )
        self.add_sound(str(audio_file_path))

        if create_subcaption:
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
        subcaption_aligner_id: str | None = None,
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
        subcaption_aligner_id
            The identifier of the alignment service to use for aligning subcaptions.
            If None (the default), the first one will be used.
        max_subcaption_len
            Maximum number of characters for a subcaption. Subcaptions that are longer
            are split into smaller chunks.
        subcaption_buff
            The duration between split subcaption chunks in seconds.
        prefer_splitting_after_chars
            A string of individual characters to preferentially split after.
            Defaults to punctuation marks (`".!?,;:"`).

        """
        # fast track for short text
        if len(text) <= max_subcaption_len:
            self.add_subcaption(text, duration)
            return

        # split and regroup
        if prefer_splitting_after_chars:
            splits = utils.split_after_characters(text, prefer_splitting_after_chars)
            regrouped = utils.regroup_splits(splits, max_subcaption_len)
        else:
            regrouped = [text]

        # wrap to make sure nothing exceeds max_subcaption_len
        wraps_list = [
            textwrap.wrap(group, width=max_subcaption_len) for group in regrouped
        ]

        # get alignments
        aligner = self._get_alignment_service_from_id(subcaption_aligner_id)
        flattened = list(itertools.chain.from_iterable(wraps_list))
        char_offsets = (0,) + tuple(
            itertools.accumulate(len(f) + 1 for f in flattened[:-1])
        )
        alignment_data = AlignmentData(
            raw_text=text,
            service_name=type(aligner).__name__,
            service_kwargs=aligner.service_kwargs,
        )
        logger.info("Aligning subcaption.")
        timestamps = aligner._align_chars_and_cache(
            text, tuple(char_offsets), self.tracker.audio_file_path, alignment_data
        )
        # compute durations=timestamps intervals
        ends = timestamps[1:] + (duration,)
        durations = tuple(
            end - start for start, end in zip(timestamps, ends, strict=True)
        )
        # add per chunk subcaption
        for offset, dur, chunk in zip(timestamps, durations, flattened, strict=True):
            self.add_subcaption(
                chunk,
                duration=dur - subcaption_buff,
                offset=offset,
            )

    def wait_for_narration_to_finish(self) -> None:
        """Wait until the end of the current narration."""
        duration = self.tracker.remaining_duration
        self.safe_wait(duration)

    def wait_until_bookmark(self, target_mark: str, offset: float = 0.0) -> None:
        """Wait until the scene reaches the target bookmark.

        Parameters
        ----------
        target_mark
            The mark attribute of the target bookmark.
        offset
            The time in seconds to add to the aligned bookmark timestamp. Can be used
            to fine tune the timing when the alignment service is not accurate enough.

        """
        self.safe_wait(self.tracker.duration_until_bookmark(target_mark) + offset)
        self.tracker.current_bookmark = target_mark

    def safe_wait(self, duration: float) -> None:
        """Wait for a given duration.

        The minimal waiting duration is one frame.

        Parameters
        ----------
        duration
            The time to wait for.

        """
        duration = max(1 / m.config["frame_rate"], duration)
        self.wait(duration)

    def _get_speech_service_from_id(
        self, speech_service_id: str | None
    ) -> SpeechService:
        """Return the speech service with a given id.

        Parameters
        ----------
        speech_service_id
            The identifier of the speech service to return.
            If `None`, the first one will be returned.

        Returns
        -------
        The speech service instance with the given identifier.

        """
        if self.speech_services == {}:
            raise SpeechServiceError(
                "Before adding a narration, you must first set a speech service using "
                "`set_speech_services`."
            )
        speech_service_id = speech_service_id or next(iter(self.speech_services))
        try:
            speech_service = self.speech_services[speech_service_id]
        except KeyError:
            raise SpeechServiceError(
                f"`{speech_service_id}` is not a known speech service. If you mean to "
                "pass text to the default service, do it as a keyword argument "
                '(`text="..."`).'
            ) from None
        return speech_service

    def _get_alignment_service_from_id(
        self, alignment_service_id: str | None
    ) -> AlignmentService:
        """Return the alignment service with a given id.

        Parameters
        ----------
        alignment_service_id
            The identifier of the alignement service to return.
            If `None`, the first one will be returned.

        Returns
        -------
        The alignment service instance with the given identifier.

        """
        alignment_service_id = alignment_service_id or next(
            iter(self.alignment_services)
        )
        try:
            alignment_service = self.alignment_services[alignment_service_id]
        except KeyError:
            raise AlignmentError(
                f"`{alignment_service_id}` is not a known alignment service. If you "
                "mean to pass text to the speech service, do it as a keyword argument "
                '(`text="..."`).'
            ) from None
        return alignment_service

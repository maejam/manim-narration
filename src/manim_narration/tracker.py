import typing as t
from pathlib import Path

from manim_narration.alignment.aligner_base import AlignmentError, AlignmentService
from manim_narration.audio_utils import get_duration

if t.TYPE_CHECKING:
    from manim_narration.narration_scene import NarrationScene


class NarrationTracker:
    """Track the progress of a narration.

    Parameters
    ----------
    raw_text
        The text to narrate, including the bookmarks.
    audio_file_path
        The path to the tracked audio file.

    """

    def __init__(
        self,
        raw_text: str,
        audio_file_path: Path,
    ) -> None:
        self.raw_text = raw_text
        self.audio_file_path = audio_file_path

        self.current_bookmark = "_origin_"
        self.bookmark_timestamps: dict[str, float] = {}

    def __str__(self) -> str:
        max_len = 50
        res = f'{type(self).__name__}(text="{self.raw_text[:max_len]}")'
        if len(self.raw_text) > max_len:
            res += " [...]"
        return res

    def _start(
        self, scene: "NarrationScene", alignment_service: AlignmentService
    ) -> None:
        """Start the tracker.

        Parameters
        ----------
        scene
            The scene this tracker belongs to.
        alignment_service
            The service used to align the bookmarks for this narration.

        """
        self.scene = scene
        self.alignment_service = alignment_service
        self.start_time = scene.time
        self.duration = (
            get_duration(self.audio_file_path)
            if not self.scene.skip_narrations
            else self.scene.skipped_narrations_duration
        )
        self.end_time = self.start_time + self.duration

    @property
    def remaining_duration(self) -> float:
        """Return the remaining duration for this narration.

        Returns
        -------
        The remaining duration for this narration in seconds.

        """
        remaining_duration: float = max((self.end_time - self.scene.time), 0.0)
        return remaining_duration

    def duration_until_bookmark(self, target_mark: str) -> float:
        """Return the duration until a given bookmark.

        Parameters
        ----------
        target_mark
            The mark attribute of the targeted bookmark.

        Returns
        -------
        The duration in seconds until the targeted bookmark is reached.

        """
        # if aligner has not been called yet, do it
        bk_ts = self.bookmark_timestamps
        if bk_ts == {}:
            bk_ts = self.alignment_service._align_bookmarks(
                self.raw_text, self.audio_file_path, self.duration
            )
            bk_ts = {"_origin_": 0.0, **bk_ts}
            self.bookmark_timestamps = bk_ts

        # retrieve current and target bookmarks timestamps
        current_bk_ts = bk_ts[self.current_bookmark]
        try:
            target_bk_ts = bk_ts[target_mark]
        except KeyError as e:
            raise AlignmentError(
                f"The bookmark `{target_mark}` does not exist. "
                "Did you forget to capture the current narration in a variable ? "
                "(`with self.narration(...) as narration:`)"
            ) from e

        duration = target_bk_ts - current_bk_ts
        return duration

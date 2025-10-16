import typing as t
from pathlib import Path

from manim_narration.alignment.aligner_base import AlignmentError
from manim_narration.audio_utils import get_duration

if t.TYPE_CHECKING:
    from manim_narration.narration_scene import NarrationScene


class NarrationTracker:
    """Track the progress of a narration.

    Parameters
    ----------
    start_time
        The time elapsed since the beginning of the scene when the tracker is created
        (as returned by `scene.time`).
    raw_text
        The text to narrate, including the bookmarks.
    audio_file_path
        The path to the tracked audio file.

    """

    def __init__(
        self,
        scene: "NarrationScene",
        start_time: float,
        raw_text: str,
        audio_file_path: Path,
    ) -> None:
        self.scene = scene
        self.raw_text = raw_text
        self.audio_file_path = audio_file_path

        self.start_time = start_time
        self.duration = get_duration(self.audio_file_path)
        self.end_time = self.start_time + self.duration
        self.current_bookmark = "_origin_"
        self.bookmark_timestamps: dict[str, float] = {}

    @property
    def remaining_duration(
        self,
    ) -> float:
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
            bk_ts = self.scene.alignment_service._align_bookmarks(
                self.raw_text, self.audio_file_path
            )
            bk_ts = {"_origin_": 0.0, **bk_ts}
            self.bookmark_timestamps = bk_ts

        # retrieve current and target bookmarks timestamps
        current_bk_ts = bk_ts[self.current_bookmark]
        try:
            target_bk_ts = bk_ts[target_mark]
        except KeyError as e:
            raise AlignmentError(f"The bookmark `{target_mark}` does not exist.") from e

        duration = target_bk_ts - current_bk_ts
        return duration

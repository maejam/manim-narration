from pathlib import Path

import manim_narration.audio_utils as audio


class NarrationTracker:
    """Track the progress of a narration.

    Parameters
    ----------
    current_time
        The time elapsed since the beginning of the scene
        (as returned by `scene.time`).
    audio_file_path
        The path to the tracked audio file.

    """

    def __init__(self, current_time: float, audio_file_path: Path) -> None:
        self.audio_file_path = audio_file_path
        self.start_time = current_time
        self.duration = audio.get_duration(self.audio_file_path)
        self.end_time = self.start_time + self.duration

    def get_remaining_duration(
        self,
        current_time: float,
    ) -> float:
        """Return the remaining duration for this narration.

        Parameters
        ----------
        current_time
            The time elapsed since the beginning of the scene
            (as returned by `scene.time`).

        Returns
        -------
        The remaining duration for this narration in seconds.

        """
        return max((self.end_time - current_time), 0)

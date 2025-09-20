from pathlib import Path

from pydantic import Field

from .base import PhField, PlaceholderModel, PlaceholderSettings


class Cache(PlaceholderModel):
    """Configuration options in the cache section."""

    dir: Path | str = PhField("{media_dir}/narrations")


class NarrationConfig(PlaceholderSettings):
    """The root section."""

    cache: Cache = Field(default_factory=Cache)

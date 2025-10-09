from collections.abc import Mapping
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from .config_base import PhField, PlaceholderModel, PlaceholderSettings


class Cache(PlaceholderModel):
    """Configuration options in the cache section."""

    dir: Path | str = PhField("{media_dir}/narrations")
    audio_file_base_name: str = "speech"
    hash_algo: str = "sha256"
    hash_len: int = -1


class TagsMapping(BaseModel):
    """Define the keys for the Tags.mapping option."""

    model_config = ConfigDict(
        extra="forbid", validate_assignment=True, validate_default=True
    )
    bookmark: str = "bookmark"


class Tags(PlaceholderModel):
    """Configuration options in the tags section."""

    _mapping: TagsMapping = PrivateAttr(default_factory=TagsMapping)

    @property
    def mapping(self) -> dict[str, str]:
        """Expose _mapping as a dictionary and not an instance."""
        return self._mapping.model_dump()

    @mapping.setter
    def mapping(self, value: Mapping[str, str]) -> None:
        """Set _mapping through a dictionary."""
        self._mapping = TagsMapping(**value)

    @property
    def all_tags(self) -> set[str]:
        """Expose _mapping values as a set."""
        return set(self._mapping.model_dump().values())


class NarrationConfig(PlaceholderSettings):
    """The root section."""

    cache: Cache = Field(default_factory=Cache)
    tags: Tags = Field(default_factory=Tags)

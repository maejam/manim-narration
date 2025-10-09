from enum import Enum
from html.parser import HTMLParser


class Default(Enum):
    token = 0


DEFAULT = (
    Default.token
)  # sentinel: https://github.com/python/typing/issues/236#issuecomment-227180301


class TagInfo:
    """Record info on parsed tags.

    When a text is parsed for tags, an instance of this class is created for each
    recorded tag.

    Parameters
    ----------
    kind
        The kind of tag. One of: "start" (`<name...>`), "end" (`</name>`)
        or "startend" (`<name.../>`).
    name
        The tag name as it appears in the source text.
    attrs
        The tag attributes as a dictionary (empty dictionary for end tags).
    offset
        The index of the character following the tag in the original text.
        The `offset` of a tag at the very beginning of the text will be 0.
        The `offset` of a tag at the very end of the text will be `len(text)`.
        If multiple consecutive tags appear in the text, their offsets will be the same.

    """

    __slots__ = ("kind", "name", "attrs", "offset")

    def __init__(
        self,
        kind: str,
        name: str,
        attrs: dict[str, str | None],
        offset: int,
    ) -> None:
        self.kind = kind
        self.name = name
        self.attrs = {} if kind == "end" else attrs
        self.offset = offset

    def __eq__(self, other: object, /) -> bool:
        return type(self) is type(other) and all(
            getattr(self, slot) == getattr(other, slot) for slot in type(self).__slots__
        )

    def __str__(self) -> str:
        if self.kind == "end":
            return f"</{self.name}>"
        elif self.kind == "startend":
            return f"<{self.name}{self.format_attrs()}/>"
        else:  # start
            return f"<{self.name}{self.format_attrs()}>"

    def format_attrs(self) -> str:
        if not self.attrs:
            return ""
        return " " + " ".join(f'{k}="{v}"' for k, v in self.attrs.items())

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(kind='{self.kind}', name='{self.name}', "
            f"attrs={self.attrs!r}, offset={self.offset})"
        )


class TagParser(HTMLParser):
    """Parse a text containing arbitrary HTML‑like tags.

    Parameters
    ----------
    tags_to_record
        A set of names for tags that will be recorded in the `tags` list. If the empty
        set is passed (the default), all tags will be recorded, if `None`, no tag will
        be recorded.
    tags_to_remove
        A set of names for tags that will be removed from the text. Any tag not in that
        set will be left in the original text. If the empty set is passed (the dfault),
        all tags will be removed. If `None`, no tag will be removed.

    Attributes
    ----------
    text
        The original text as a string with every tag in `tags_to_remove` stripped away.
    text_parts
        The original text as a list split where each removed tag used to be.
    tags
        A list of the recorded TagInfo objects in the order they appeared.

    """

    def __init__(
        self,
        tags_to_record: set[str] | None | Default = DEFAULT,
        tags_to_remove: set[str] | None | Default = DEFAULT,
    ) -> None:
        super().__init__()
        self.tags_to_record = tags_to_record if tags_to_record is not DEFAULT else set()
        self.tags_to_remove = tags_to_remove if tags_to_remove is not DEFAULT else set()
        self.text_parts: list[str] = []  # fragments of raw text
        self.tags: list[TagInfo] = []  # discovered tags
        self._pos = 0

    def _process_tag(self, kind: str, tag: str, attrs: dict[str, str | None]) -> None:
        tag_info = TagInfo(kind, tag, attrs, self._pos)
        if self.tags_to_record is not None and (
            not self.tags_to_record or tag in self.tags_to_record
        ):
            self.tags.append(tag_info)
        if self.tags_to_remove is None or (
            self.tags_to_remove and tag not in self.tags_to_remove
        ):
            self.text_parts.append(str(tag_info))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._process_tag("start", tag, dict(attrs))

    def handle_endtag(self, tag: str) -> None:
        self._process_tag("end", tag, {})

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._process_tag("startend", tag, dict(attrs))

    def handle_data(self, data: str) -> None:
        self.text_parts.append(data)
        self._pos += len(data)

    @property
    def text(self) -> str:
        """The input string with all considered tags removed."""
        return "".join(self.text_parts)

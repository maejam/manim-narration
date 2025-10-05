from html.parser import HTMLParser


class TagInfo:
    """Info on discovered tags.

    When a text is parsed for tags, an instance of this class is created for each
    discovered tag.

    Parameters
    ----------
    type_
        The type of tag: "start" (`<...`), "end" (`.../>`) or "startend" (`<.../>`).
    name
        The tag name as it appears in the source text.
    attrs
        The tag attributes as a dictionary (empty dictionary for end tags).

    """

    __slots__ = ("type", "name", "attrs")

    def __init__(
        self, type_: str, name: str, attrs: dict[str, str | None] | None = None
    ):
        self.type = type_
        self.name = name
        self.attrs = attrs or {}

    def __eq__(self, other: object, /) -> bool:
        return type(self) is type(other) and all(
            getattr(self, slot) == getattr(other, slot) for slot in type(self).__slots__
        )

    def __repr__(self) -> str:
        if self.type == "end":
            return f"</{self.name}>"
        elif self.type == "startend":
            return f"<{self.name}{self.format_attrs()}/>"
        else:  # start
            return f"<{self.name}{self.format_attrs()}>"

    def format_attrs(self) -> str:
        if not self.attrs:
            return ""
        return " " + " ".join(f'{k}="{v}"' for k, v in self.attrs.items())


class TagParser(HTMLParser):
    """Parse a text containing arbitrary HTML‑like tags.

    Parameters
    ----------
    tags_to_consider
        A tuple of tags that will be extracted from the parsed text. Any tag not in that
        tuple will be left in the original text. If the empy tuple is passed
        (the dfault), all tags will be considered.

    Attributes
    ----------
    text
        The original text with every considered tags stripped away.
    tags
        The extracted TagInfo objects in the order they appeared.

    """

    def __init__(self, tags_to_consider: set[str] | None = None):
        super().__init__()
        self.tags_to_consider = tags_to_consider or set()
        self.text_parts: list[str] = []  # fragments of raw text
        self.tags: list[TagInfo] = []  # discovered tags

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_info = TagInfo("start", tag, dict(attrs))
        if tag in self.tags_to_consider or self.tags_to_consider == set():
            self.tags.append(tag_info)
        else:
            self.text_parts.append(repr(tag_info))

    def handle_endtag(self, tag: str) -> None:
        tag_info = TagInfo("end", tag)
        if tag in self.tags_to_consider or self.tags_to_consider == set():
            self.tags.append(tag_info)
        else:
            self.text_parts.append(repr(tag_info))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_info = TagInfo("startend", tag, dict(attrs))
        if tag in self.tags_to_consider or self.tags_to_consider == set():
            self.tags.append(tag_info)
        else:
            self.text_parts.append(repr(tag_info))

    def handle_data(self, data: str) -> None:
        self.text_parts.append(data)

    @property
    def text(self) -> str:
        """The input string with all considered tags removed."""
        return "".join(self.text_parts)

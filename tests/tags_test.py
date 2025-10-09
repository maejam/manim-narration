import pytest

from manim_narration.tags import TagInfo, TagParser

tags = {"bookmark", "foo", "bar"}


@pytest.fixture
def parser():
    parser = TagParser()
    return parser


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("start", '<tag k1="v1" k2="v2">'),
        ("end", "</tag>"),
        ("startend", '<tag k1="v1" k2="v2"/>'),
    ],
)
def test_TagInfo_str(kind, expected):
    assert str(TagInfo(kind, "tag", {"k1": "v1", "k2": "v2"}, 0)) == expected


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        (
            "start",
            "TagInfo(kind='start', name='tag', attrs={'k1': 'v1', 'k2': 'v2'}, "
            "offset=0)",
        ),
        ("end", "TagInfo(kind='end', name='tag', attrs={}, offset=0)"),
        (
            "startend",
            "TagInfo(kind='startend', name='tag', attrs={'k1': 'v1', 'k2': 'v2'}, "
            "offset=0)",
        ),
    ],
)
def test_TagInfo_repr(kind, expected):
    tag = TagInfo(kind, "tag", {"k1": "v1", "k2": "v2"}, 0)
    assert repr(tag) == expected
    assert eval(repr(tag)) == tag


def test_TagInfo_eq():
    assert TagInfo("start", "tag", {}, 0) == TagInfo("start", "tag", {}, 0)
    assert TagInfo("start", "tag", {"attr": "value"}, 0) == TagInfo(
        "start", "tag", {"attr": "value"}, 0
    )
    assert TagInfo("startend", "tag", {}, 0) != TagInfo("start", "tag", {}, 0)
    assert TagInfo("start", "tag2", {}, 0) != TagInfo("start", "tag", {}, 0)
    assert TagInfo("start", "tag", {"attr": "value"}, 0) != TagInfo(
        "start", "tag", {}, 0
    )
    assert TagInfo("start", "tag", {"attr": "value"}, 0) != TagInfo(
        "start", "tag", {}, 1
    )


@pytest.mark.parametrize(
    ("record", "remove"),
    [
        (None, None),
        (None, set()),
        (None, set("b")),
        (set(), None),
        (set(), set()),
        (set(), set("b")),
        (set("a"), None),
        (set("a"), set()),
        (set("a"), set("b")),
    ],
)
def test_TagParser_without_tags(parser, record, remove):
    text = "This is just a test string."
    parser.tags_to_record = record
    parser.tags_to_remove = remove
    parser.feed(text)
    assert parser.text == text
    assert parser.tags == []


def test_TagParser_works_with_all_kind(parser):
    parser.feed(
        "The <foo k='vfoo'/>quick <bar k=vbar>brown</bar> fox jumps over the lazy dog."
    )
    assert parser.text == "The quick brown fox jumps over the lazy dog."
    assert parser.tags == [
        TagInfo("startend", "foo", {"k": "vfoo"}, 4),
        TagInfo("start", "bar", {"k": "vbar"}, 10),
        TagInfo("end", "bar", {}, 15),
    ]


@pytest.mark.parametrize(
    "text",
    [
        "This is <a/>a test.",
        "<b/>This is a test.",
        "This is a test.<c/>",
        "This <d>is</d> a test.",
    ],
)
def test_TagParser_with_tags_to_remove_None(parser, text):
    parser.tags_to_remove = None
    parser.feed(text)
    assert parser.text == text


@pytest.mark.parametrize(
    "text",
    [
        "This is <a/>a test.",
        "<b/>This is a test.",
        "This is a test.<c/>",
        "This <d>is</d> a test.",
    ],
)
def test_TagParser_with_tags_to_record_None(parser, text):
    parser.tags_to_record = None
    parser.feed(text)
    assert parser.tags == []


@pytest.mark.parametrize(
    "text",
    [
        "This is <a/>a test.",
        "<b/>This is a test.",
        "This is a test.</c>",
        "This <d>is</d> a test.",
    ],
)
def test_TagParser_with_tags_to_remove_all(parser, text):
    parser.tags_to_remove = set()
    parser.feed(text)
    assert parser.text == "This is a test."


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("This is <a/>a test.", [TagInfo("startend", "a", {}, 8)]),
        ("<b/>This is a test.", [TagInfo("startend", "b", {}, 0)]),
        ("This is a test.</c>", [TagInfo("end", "c", {}, 15)]),
        (
            "This <d>is</d> a test.",
            [TagInfo("start", "d", {}, 5), TagInfo("end", "d", {}, 7)],
        ),
    ],
)
def test_TagParser_with_tags_to_record_all(parser, text, expected):
    parser.tags_to_record = set()
    parser.feed(text)
    assert parser.tags == expected


@pytest.mark.parametrize(
    "text",
    [
        "This is <a/>a test.",
        "<b/>This is a test.",
        "This is a test.<c/>",
        "This <d>is</d> a test.",
    ],
)
def test_TagParser_with_tags_to_remove_defaults_to_all(parser, text):
    parser.feed(text)
    assert parser.text == "This is a test."


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("This is <a/>a test.", [TagInfo("startend", "a", {}, 8)]),
        ("<b/>This is a test.", [TagInfo("startend", "b", {}, 0)]),
        ("This is a test.</c>", [TagInfo("end", "c", {}, 15)]),
        (
            "This <d>is</d> a test.",
            [TagInfo("start", "d", {}, 5), TagInfo("end", "d", {}, 7)],
        ),
    ],
)
def test_TagParser_with_tags_to_record_defaults_to_all(parser, text, expected):
    parser.feed(text)
    assert parser.tags == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("This is <foo/>a<baz/> test.", "This is a<baz/> test."),
        ("<bar/>This is a</baz> test.", "This is a</baz> test."),
        ("This is a test.<baz><foo/></baz>", "This is a test.<baz></baz>"),
        ("This </foo>is</bar><baz> a test.", "This is<baz> a test."),
    ],
)
def test_TagParser_with_tags_to_remove_subset(parser, text, expected):
    parser.tags_to_remove = tags
    parser.feed(text)
    assert parser.text == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("This is <foo/>a<baz/> test.", [TagInfo("startend", "foo", {}, 8)]),
        ("<bar/>This is a</baz> test.", [TagInfo("startend", "bar", {}, 0)]),
        ("This is a test.<baz><foo></baz>", [TagInfo("start", "foo", {}, 15)]),
        (
            "This </foo>is</bar><baz> a test.",
            [TagInfo("end", "foo", {}, 5), TagInfo("end", "bar", {}, 7)],
        ),
    ],
)
def test_TagParser_with_tags_to_record_subset(parser, text, expected):
    parser.tags_to_record = tags
    parser.feed(text)
    assert parser.tags == expected

import pytest

from manim_narration.tags import TagInfo, TagParser

tags = {"bookmark", "foo", "bar"}


@pytest.fixture
def parser():
    parser = TagParser()
    return parser


@pytest.mark.parametrize(
    ("type_", "expected"),
    [
        ("start", '<tag k1="v1" k2="v2">'),
        ("end", "</tag>"),
        ("startend", '<tag k1="v1" k2="v2"/>'),
    ],
)
def test_TagInfo_repr(type_, expected):
    assert repr(TagInfo(type_, "tag", {"k1": "v1", "k2": "v2"})) == expected


def test_TagInfo_eq():
    assert TagInfo("start", "tag", {}) == TagInfo("start", "tag", {})
    assert TagInfo("start", "tag", {"attr": "value"}) == TagInfo(
        "start", "tag", {"attr": "value"}
    )
    assert TagInfo("startend", "tag", {}) != TagInfo("start", "tag", {})
    assert TagInfo("start", "tag2", {}) != TagInfo("start", "tag", {})
    assert TagInfo("start", "tag", {"attr": "value"}) != TagInfo("start", "tag", {})


def test_TagParser_without_tags(parser):
    text = "This is just a test string."
    parser.feed(text)
    assert parser.text == text
    assert parser.tags == []


@pytest.mark.parametrize(
    "text",
    [
        "This is <gghghg/>a test.",
        "<gghghg/>This is a test.",
        "This is a test.<gghghg/>",
        "This <gghghg>is</gghghg> a test.",
    ],
)
def test_TagParser_does_not_remove_non_considered_tags(parser, text):
    parser.tags_to_consider = tags
    parser.feed(text)
    assert parser.text == text
    assert parser.tags == []


@pytest.mark.parametrize(
    ("text", "expected_txt", "expected_tags"),
    [
        (
            "This is a <bookmark mark='test'/>.",
            "This is a .",
            [TagInfo("startend", "bookmark", {"mark": "test"})],
        ),
        ("And another<foo/>one", "And anotherone", [TagInfo("startend", "foo", {})]),
    ],
)
def test_TagParser_works_with_only_one_tag(parser, text, expected_txt, expected_tags):
    parser.tags_to_consider = tags
    parser.feed(text)
    assert parser.text == expected_txt
    assert parser.tags == expected_tags


@pytest.mark.parametrize(
    ("text", "expected_tagname"),
    [
        ("It works<bookmark />!", "bookmark"),
        ("It works<foo />!", "foo"),
        ("It works<bar />!", "bar"),
    ],
)
def test_TagParser_works_with_all_declared_tags(parser, text, expected_tagname):
    parser.tags_to_consider = tags
    parser.feed(text)
    assert parser.text == "It works!"
    assert parser.tags == [TagInfo("startend", expected_tagname, {})]


@pytest.mark.parametrize(
    ("text", "expected_tagname"),
    [
        ("It works<bookmark />!", "bookmark"),
        ("It works<foo />!", "foo"),
        ("It works<bar />!", "bar"),
    ],
)
def test_TagParser_works_with_default_declared_tags(parser, text, expected_tagname):
    parser.feed(text)
    assert parser.text == "It works!"
    assert parser.tags == [TagInfo("startend", expected_tagname, {})]


@pytest.mark.parametrize(
    ("text", "expected_tagnames"),
    [
        ("It <foo/>works<bookmark />!", ["foo", "bookmark"]),
        ("It works<foo /><bar/>!", ["foo", "bar"]),
        ("<foo/>It<foo/> works<bar />!<bookmark/>", ["foo", "foo", "bar", "bookmark"]),
    ],
)
def test_TagParser_works_with_multiple_tags(parser, text, expected_tagnames):
    parser.feed(text)
    assert parser.text == "It works!"
    assert parser.tags == [TagInfo("startend", name, {}) for name in expected_tagnames]


def test_TagParser_works_with_all_tag_types(parser):
    parser.feed(
        "The <foo k='vfoo'/>quick <bar k=vbar>brown</bar> fox jumps over the lazy dog."
    )
    assert parser.text == "The quick brown fox jumps over the lazy dog."
    assert parser.tags == [
        TagInfo("startend", "foo", {"k": "vfoo"}),
        TagInfo("start", "bar", {"k": "vbar"}),
        TagInfo("end", "bar", {}),
    ]

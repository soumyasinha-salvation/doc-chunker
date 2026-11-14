from collections.abc import Iterator

import pytest

from doc_chunker.models import Chunk, Section
from doc_chunker.splitter import chunk_sections, split_text

WORDS = " ".join(f"w{i:03d}" for i in range(200))  # "w000 w001 ... w199", 999 chars


def rebuild(pieces: list[str], overlap: int) -> str:
    return pieces[0] + "".join(p[overlap:] for p in pieces[1:])


# --- argument validation ---------------------------------------------------


@pytest.mark.parametrize(
    ("size", "overlap"),
    [(0, 0), (-5, 0), (10, -1), (10, 10), (10, 11)],
)
def test_invalid_arguments_raise(size, overlap):
    with pytest.raises(ValueError):
        split_text("some text", size, overlap)


# --- simple cases ----------------------------------------------------------


def test_empty_text_gives_no_pieces():
    assert split_text("", 50, 10) == []


def test_short_text_is_returned_whole():
    assert split_text("short text", 50, 10) == ["short text"]


def test_text_exactly_size_is_one_piece():
    assert split_text("a" * 50, 50, 10) == ["a" * 50]


# --- properties on longer text ---------------------------------------------


@pytest.mark.parametrize(("size", "overlap"), [(50, 10), (120, 30), (40, 0)])
def test_no_piece_exceeds_size(size, overlap):
    pieces = split_text(WORDS, size, overlap)
    assert len(pieces) > 1
    assert all(len(p) <= size for p in pieces)


@pytest.mark.parametrize(("size", "overlap"), [(50, 10), (120, 30)])
def test_consecutive_pieces_share_exact_overlap(size, overlap):
    pieces = split_text(WORDS, size, overlap)
    for a, b in zip(pieces, pieces[1:], strict=False):
        assert a[-overlap:] == b[:overlap]


@pytest.mark.parametrize(("size", "overlap"), [(50, 10), (120, 30), (40, 0)])
def test_text_can_be_rebuilt(size, overlap):
    pieces = split_text(WORDS, size, overlap)
    assert rebuild(pieces, overlap) == WORDS


def test_words_are_not_cut_when_avoidable():
    pieces = split_text(WORDS, 50, 10)
    # every piece except the last should end right after a space
    assert all(p.endswith(" ") for p in pieces[:-1])


def test_text_without_whitespace_is_cut_hard():
    text = "a" * 120
    pieces = split_text(text, 50, 10)
    assert pieces[0] == "a" * 50
    assert all(len(p) <= 50 for p in pieces)
    assert rebuild(pieces, 10) == text


# --- chunk_sections ----------------------------------------------------------


def test_chunk_sections_is_a_generator():
    result = chunk_sections([Section("A", "text")], "f.md", 50, 10)
    assert isinstance(result, Iterator)


def test_chunk_sections_labels_and_indexes():
    sections = [Section("A", WORDS[:120]), Section("B", "short")]
    chunks = list(chunk_sections(sections, "docs/f.md", 50, 10))

    assert all(isinstance(c, Chunk) for c in chunks)
    assert [c.index for c in chunks] == list(range(len(chunks)))
    assert {c.source for c in chunks} == {"docs/f.md"}
    assert chunks[0].section == "A"
    assert chunks[-1] == Chunk(text="short", source="docs/f.md", section="B", index=len(chunks) - 1)


def test_chunk_sections_with_no_sections():
    assert list(chunk_sections([], "f.md", 50, 10)) == []

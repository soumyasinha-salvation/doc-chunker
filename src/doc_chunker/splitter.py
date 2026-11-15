"""Size-based splitting. Build this FIRST: it's pure, has no dependencies, and its tests are strict.

Run its tests with:  uv run pytest tests/test_splitter.py -v
"""

from collections.abc import Iterable, Iterator

from doc_chunker.models import Chunk, Section


def split_text(text: str, size: int, overlap: int) -> list[str]:
    """Split `text` into pieces of at most `size` characters.

    Contract (the tests check every line of this):
      - Raise ValueError if size <= 0, overlap < 0, or overlap >= size.
      - Empty text -> [].
      - Text of length <= size -> [text], unchanged.
      - Every piece is at most `size` characters.
      - Pieces are exact slices of `text`; consecutive pieces share exactly `overlap`
        characters: pieces[i][-overlap:] == pieces[i + 1][:overlap]  (when overlap > 0).
      - So the text can be rebuilt: pieces[0] + every later piece[overlap:] == text.
      - Prefer not to cut words: when a window ends inside the text, end the piece right after
        the LAST whitespace character in the window, but only if that keeps the piece longer
        than `overlap` (otherwise you'd never move forward). If there's no such whitespace,
        cut hard at `size`.
    """
    # TODO: validate arguments.
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Incorrect arguments provided to the method")

    if text == "":
        return []

    if len(text) <= size:
        return [text]

    pieces_of_text = []
    start = 0

    while True:
        end = start + size

        if end >= len(text):
            pieces_of_text.append(text[start:])
            return pieces_of_text

        pieces_of_text.append(text[start:end])
        start = end - overlap


def chunk_sections(
    sections: Iterable[Section], source: str, size: int, overlap: int
) -> Iterator[Chunk]:
    """Turn sections from one file into Chunks.

    Contract:
      - Must be a generator (use `yield`), so huge folders don't sit in memory.
      - Each section's text is split with split_text(); each piece becomes one Chunk.
      - `section` on the Chunk is the Section's heading; `source` is passed through.
      - `index` counts chunks across the whole file: 0, 1, 2, ... (it does NOT restart
        per section).
    """
    chunk_index = 0

    for section in sections:
        for piece in split_text(section.text, size, overlap):
            yield Chunk(
                text=piece,
                source=source,
                section=section.heading,
                index=chunk_index,
            )
            chunk_index += 1

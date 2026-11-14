"""Data model. This file is complete: read it, then build everything else on top of it."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Section:
    """A piece of a document under one heading path, before size-based splitting.

    heading: the heading path, e.g. "Installation > Linux", "page 3", or "" if none.
    text:    the section's body text, stripped of leading and trailing whitespace.
    """

    heading: str
    text: str


@dataclass(frozen=True)
class Chunk:
    """One output record. One Chunk becomes one line of JSONL."""

    text: str
    source: str  # file path the chunk came from
    section: str  # heading path of the section it came from
    index: int  # position of the chunk within its file, starting at 0

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)

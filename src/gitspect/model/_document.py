from collections.abc import Sequence
from dataclasses import dataclass

__all__ = ["Segment", "Document"]


@dataclass(frozen=True)
class Segment:
    start: int
    end: int

    def __eq__(self, other):
        return (
            isinstance(other, Segment)
            and self.start == other.start
            and self.end == other.end
        )


class Document:
    def __init__(self, lines: Sequence[str], segments: Sequence[Segment]):
        self._lines = lines
        self._segments = segments

    def segments(self) -> Sequence[Segment]:
        return self._segments

    def __iter__(self):
        for s in self._segments:
            yield self._lines[s.start : s.end]

from collections.abc import Sequence, Iterable
from dataclasses import dataclass
from pathlib import Path
import logging
from ._utils import LineIndent, indent_len

__all__ = ["Segment", "Document", "PythonSegmenter"]


logging.basicConfig(encoding="utf-8", level=logging.INFO)
logger = logging.getLogger(__name__)


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


class PythonSegmenter:
    def __init__(self, lines: Iterable[str]):
        self._lines = lines

    @classmethod
    def from_path(cls, file_path: Path):
        return cls(file_path.read_text().split("\n"))

    def segment(self) -> Document:
        lines = list(self._lines)
        non_empty_li = 0
        indents = []
        segments = []

        if not lines:
            return Document([], [])

        line_indent = indent_len(lines[0])
        logger.debug("Indent %d at %d", line_indent, 0)
        indents.append(LineIndent(0, line_indent))

        for li, line in enumerate(lines[1:], 1):
            if not line.strip():
                continue
            line_indent = indent_len(line)
            if line_indent > indents[-1].indent:
                logger.debug("Indent %d at %d", line_indent, li)
                indents.append(LineIndent(li, line_indent))
            else:
                while line_indent < indents[-1].indent:
                    start = indents.pop()
                    if _valid_segment_start(lines[start.li - 1]):
                        segments.append(
                            Segment(
                                _line_lookback(lines, start.li - 1), non_empty_li + 1
                            )
                        )
                        logger.debug("Creating segment: %s", segments[-1])
                    else:
                        logger.debug(
                            "Skipping segment starting with: '%s'", lines[start.li - 1]
                        )
            non_empty_li = li

        while indents:
            start = indents.pop()
            if _valid_segment_start(lines[start.li - 1]):
                segments.append(
                    Segment(_line_lookback(lines, start.li - 1), non_empty_li + 1)
                )
                logger.debug("Creating segment: %s", segments[-1])
            else:
                logger.debug(
                    "Skipping segment starting with: '%s'", lines[start.li - 1]
                )
        segments.append(Segment(0, non_empty_li))
        return Document(lines, segments)


def _valid_segment_start(line: str) -> bool:
    return any(line.strip().startswith(x) for x in ["class", "def"])


def _line_lookback(lines: Sequence[str], start_index: int) -> int:
    start_indent = indent_len(lines[start_index])
    for lookback_line in reversed(lines[:start_index]):
        if lookback_line.strip() and indent_len(lookback_line) >= start_indent:
            start_index -= 1
        else:
            break
    return start_index

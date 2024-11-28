from collections.abc import Sequence, Iterable
from pathlib import Path
import logging
from ._utils import LineIndent, indent_len
from gitspect.model import Document, Segment

__all__ = ["PythonSegmenter"]


logging.basicConfig(encoding="utf-8", level=logging.INFO)
logger = logging.getLogger(__name__)


class PythonSegmenter:
    def __init__(self, document_name: str, lines: Iterable[str]):
        self._document_name = document_name
        self._lines = lines

    @classmethod
    def from_path(cls, file_path: Path):
        return cls(str(file_path), file_path.read_text().split("\n"))

    def segment(self) -> Document:
        lines = list(self._lines)
        non_empty_li = 0
        indents = []
        segments = []

        if not lines:
            return Document(self._document_name, [], [])

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
                while line_indent < indents[-1].indent and not _closing_function_def(
                    line
                ):
                    segment = _create_segment(
                        self._document_name, lines, indents.pop(), non_empty_li
                    )
                    if segment:
                        logger.debug("Creating segment: %s", segment)
                        segments.append(segment)
            non_empty_li = li

        while indents:
            segment = _create_segment(
                self._document_name, lines, indents.pop(), non_empty_li
            )
            if segment:
                logger.debug("Creating segment: %s", segment)
                segments.append(segment)
        segments.append(
            Segment(start=0, end=non_empty_li, document_name=self._document_name)
        )
        return Document(
            document_name=self._document_name, lines=lines, segments=segments
        )


def _closing_function_def(line):
    # This assumes BLACK formatting
    return line.strip().startswith(")") and line.strip().endswith(":")


def _create_segment(
    document_name: str, lines: list[str], start: LineIndent, non_empty_li: int
) -> Segment | None:
    if _valid_segment_start(lines[start.li - 1]):
        return Segment(
            start=_lookback_index(lines, start.li - 1),
            end=non_empty_li + 1,
            document_name=document_name,
        )
    else:
        logger.debug("Skipping segment starting with: '%s'", lines[start.li - 1])
        return None


def _valid_segment_start(line: str) -> bool:
    return any(line.strip().startswith(x) for x in ["class", "def"])


def _lookback_index(lines: Sequence[str], start_index: int) -> int:
    start_indent = indent_len(lines[start_index])
    for lookback_line in reversed(lines[:start_index]):
        if lookback_line.strip() and indent_len(lookback_line) >= start_indent:
            start_index -= 1
        else:
            break
    return start_index

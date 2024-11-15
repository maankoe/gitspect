from collections import namedtuple

__all__ = ["LineIndent", "indent_len"]

LineIndent = namedtuple("LineIndent", "li, indent")


def indent_len(line: str, tab_len: int = 4) -> int:
    spaced_indent = line.expandtabs(tab_len)
    return (
        0
        if spaced_indent.isspace()
        else len(spaced_indent) - len(spaced_indent.lstrip())
    )

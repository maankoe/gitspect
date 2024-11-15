import unittest
from pathlib import Path
import inspect

from gitspect.segmentation.python_segmentation import (
    PythonSegmenter,
    _line_lookback,
    Segment,
)
from gitspect.segmentation import python_segmentation


class TestPythonSegmenter(unittest.TestCase):
    document = PythonSegmenter.from_path(Path(python_segmentation.__file__)).segment()

    def test_line_lookback(self):
        self.assertEqual(_line_lookback(["  ", "b"], 1), 1)
        self.assertEqual(_line_lookback([" \t ", "b"], 1), 1)
        self.assertEqual(_line_lookback(["A", " \t ", "b"], 2), 2)
        self.assertEqual(_line_lookback(["  ", " a ", "b"], 2), 1)
        self.assertEqual(_line_lookback(["  a", "b"], 1), 0)
        self.assertEqual(_line_lookback(["@a(", "   b", ")", "c"], 3), 0)

    def test_module_segment(self):
        source_lines = inspect.getsourcelines(python_segmentation)
        expected = Segment(source_lines[1], source_lines[1] + len(source_lines[0]) - 1)
        print(source_lines)
        self.assertIn(expected, self.document.segments())

    def test_class_segments(self):
        for x in inspect.getmembers(
            python_segmentation,
            lambda m: inspect.isclass(m)
            and python_segmentation.__name__ in m.__module__,
        ):
            source_lines = inspect.getsourcelines(x[1])
            expected = Segment(
                source_lines[1] - 1, source_lines[1] + len(source_lines[0]) - 1
            )
            self.assertIn(expected, self.document.segments())

    def test_function_segments(self):
        for x in inspect.getmembers(
            python_segmentation,
            lambda m: inspect.isfunction(m)
            and python_segmentation.__name__ in m.__module__,
        ):
            source_lines = inspect.getsourcelines(x[1])
            expected = Segment(
                source_lines[1] - 1, source_lines[1] + len(source_lines[0]) - 1
            )
            self.assertIn(expected, self.document.segments())

    def test_class_method_segments(self):
        for x in inspect.getmembers(
            python_segmentation.Document,
            lambda m: inspect.isfunction(m)
            and python_segmentation.__name__ in m.__module__,
        ):
            source_lines = inspect.getsourcelines(x[1])
            expected = Segment(
                source_lines[1] - 1, source_lines[1] + len(source_lines[0]) - 1
            )
            self.assertIn(expected, self.document.segments())
        print(self.document.segments())

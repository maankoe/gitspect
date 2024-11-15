import unittest

from gitspect.segmentation._utils import indent_len


class TestSegmentationUtils(unittest.TestCase):
    def test_indent_len(self):
        self.assertEqual(indent_len("a."), 0)
        self.assertEqual(indent_len("  a\t"), 2)
        self.assertEqual(indent_len("   a"), 3)
        self.assertEqual(indent_len("    a "), 4)
        self.assertEqual(indent_len("\ta  ", 5), 5)

import unittest
from unittest import mock

from transcriber.converter.utils import determine_total_tags


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.filenames = ["this", "is", "a", "test"]

    @mock.patch("transcriber.dbf.parser.Parser.parse_all")
    def test_determine_total_tags(self, mock_parser):
        gen_dict = lambda x: {"TagIndex": x}
        mock_parser.return_value = [gen_dict(i) for i in range(3)] * 2
        for _, total_tags in determine_total_tags(self.filenames):
            self.assertEqual(total_tags, 3)

    @mock.patch("transcriber.dbf.parser.Parser.parse_all")
    def test_determine_total_tags_key_error(self, mock_parser):
        mock_parser.return_value = [{"Value": 404}]
        for _, total_tags in determine_total_tags(self.filenames):
            self.assertEqual(total_tags, 0)

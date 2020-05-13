import io
import struct
import unittest
from unittest import mock

from transcriber.converter.dbfworker import utils, worker

DEFAULT_DECIMAL_PLACES = 8


def _generate_row(date, time, input_value):
    return {
        "Date": date,
        "Time": time,
        "Value": struct.pack("<d", input_value),
    }


class TestDBFWorker(unittest.TestCase):
    def setUp(self):
        config = {
            "tags": ["First", "Second", "Fifth"],
            "decimal_places": DEFAULT_DECIMAL_PLACES,
        }
        self.worker = worker.DBFWorker(
            filename="filename",
            tag_lookup=["First", "Second", "Third", "Fourth", "Fifth"],
            **config,
        )
        self.test_table = [
            _generate_row(b"19700101", b"00:00:00", i) for i in range(1, 4)
        ] + [_generate_row(b"19700101", b"00:00:08", i) for i in range(1, 4)]
        self.test_table_usual_output = """Date,Time,First,Second,Fifth
01/01/1970,00:00:00,1.0,2.0,3.0
01/01/1970,00:00:08,1.0,2.0,3.0"""

    def test_write_csv_writes_to_file(self):
        csv_file = io.StringIO()
        utils.write_csv(csv_file, self.worker.tags)
        csv_file.seek(0)
        self.assertEqual(csv_file.read(), "FirstSecondFifth")

    def test_write_csv_correctly_writes_after_csv_generation(self):
        csv_file = io.StringIO()
        utils.write_csv(
            csv_file,
            utils.generate_csv(
                self.test_table,
                self.worker.tags,
                self.worker.tag_lookup,
                DEFAULT_DECIMAL_PLACES,
            ),
        )
        csv_file.seek(0)
        self.assertEqual(csv_file.read(), self.test_table_usual_output)

    @mock.patch("transcriber.converter.dbfworker.utils.write_csv")
    @mock.patch("transcriber.converter.dbfworker.utils.generate_csv")
    @mock.patch("transcriber.dbf.parser.Parser.parse_selection")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_convert(
        self,
        mock_file,
        mock_parse_selection,
        mock_generate_csv,
        mock_write_csv,
    ):
        self.worker.convert()
        mock_write_csv.assert_called_with(mock_file(), mock_generate_csv())
        mock_parse_selection.assert_called_with(
            self.worker.filename, [0, 1, 4], 5
        )
        self.worker.total_tags -= 1
        self.worker.convert()
        mock_parse_selection.assert_called_with(
            self.worker.filename, [0, 1, 4], 4
        )

    def test_total_tags_is_set(self):
        _worker = worker.DBFWorker(
            filename="filename", total_tags=10, **{"tags": []}
        )
        self.assertEqual(_worker.total_tags, 10)

    def test_generate_csv(self):
        self.assertEqual(
            "".join(
                utils.generate_csv(
                    self.test_table,
                    self.worker.tags,
                    self.worker.tag_lookup,
                    DEFAULT_DECIMAL_PLACES,
                )
            ),
            self.test_table_usual_output,
        )

    def test_generate_csv_with_empty_generator(self):
        table = []
        expected = "Date,Time,First,Second,Fifth"
        self.assertEqual(
            "".join(
                utils.generate_csv(
                    table,
                    self.worker.tags,
                    self.worker.tag_lookup,
                    DEFAULT_DECIMAL_PLACES,
                )
            ),
            expected,
        )

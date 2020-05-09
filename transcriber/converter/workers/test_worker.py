import io
import struct
import unittest
from unittest import mock

from transcriber.converter.workers import worker
from transcriber.dbf.parser import Parser


def _generate_row(date, time, input_value):
    return {
        "Date": date,
        "Time": time,
        "Value": struct.pack("<d", input_value),
    }


class TestDBFWorker(unittest.TestCase):
    def setUp(self):
        self.worker = worker.DBFWorker(
            "filename",
            ["First", "Second", "Fifth"],
            ["First", "Second", "Third", "Fourth", "Fifth"],
        )
        self.test_table = [
            _generate_row(b"19700101", b"00:00:00", i) for i in range(1, 4)
        ] + [_generate_row(b"19700101", b"00:00:08", i) for i in range(1, 4)]
        self.test_table_usual_output = """Date,Time,First,Second,Fifth
01/01/1970,00:00:00,1.0,2.0,3.0
01/01/1970,00:00:08,1.0,2.0,3.0"""

    def test_write_csv_writes_to_file(self):
        csv_file = io.StringIO()
        worker.write_csv(csv_file, self.worker.tags)
        csv_file.seek(0)
        self.assertEqual(csv_file.read(), "FirstSecondFifth")

    def test_write_csv_correctly_writes_after_csv_generation(self):
        csv_file = io.StringIO()
        worker.write_csv(csv_file, self.worker.generate_csv(self.test_table))
        csv_file.seek(0)
        self.assertEqual(csv_file.read(), self.test_table_usual_output)

    @mock.patch("transcriber.converter.workers.worker.write_csv")
    @mock.patch("transcriber.converter.workers.worker.DBFWorker.generate_csv")
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

    def test_generate_csv(self):
        self.assertEqual(
            "".join(self.worker.generate_csv(self.test_table)),
            self.test_table_usual_output,
        )

    def test_generate_csv_with_empty_generator(self):
        table = []
        expected = "Date,Time,First,Second,Fifth"
        self.assertEqual("".join(self.worker.generate_csv(table)), expected)


class TestCSVWorker(unittest.TestCase):
    def setUp(self):
        pass

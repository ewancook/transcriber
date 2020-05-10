import unittest

from transcriber.converter.dbfworker import utils


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.common_lines = {
            "01/01/1970,00:00:00,000,TEST_TAG   ,123": (
                "01/01/1970",
                "00:00:00",
                "TEST_TAG",
                "123",
            ),
            "01/01/1970,00:00:00,000,TEST_TAG,123   ": (
                "01/01/1970",
                "00:00:00",
                "TEST_TAG",
                "123",
            ),
            "12/31/1970,23:59:59,999,TEST_TAG,987": (
                "31/12/1970",
                "23:59:59",
                "TEST_TAG",
                "987",
            ),
        }

    def test_data_from_line(self):
        for test_arg, expected in self.common_lines.items():
            self.assertEqual(utils.data_from_line(test_arg), expected)

    def test_flip_date(self):
        tests = {"01/02/1970": "02/01/1970", "10/11/12": "11/10/12"}
        for test_arg, expected in tests.items():
            self.assertEqual(utils.flip_date(test_arg), expected)

    def test_val_from_line(self):
        for test_arg, expected in self.common_lines.items():
            self.assertEqual(utils.val_from_line(test_arg), expected[3])

    def test_transcribed_filename(self):
        tests = {
            "username/test/DBF_NAME.DAT": "username/test/DBF_NAME (Transcribed).csv",
            "user.name/test/DBF_NAME_V.2.DAT": "user.name/test/DBF_NAME_V.2 (Transcribed).csv",
        }
        for test_arg, expected in tests.items():
            self.assertEqual(utils.transcribed_filename(test_arg), expected)

    def test_format_dbf_date(self):
        tests = {"19700101": "01/01/1970", "20121110": "10/11/2012"}
        for test_arg, expected in tests.items():
            self.assertEqual(utils.format_dbf_date(test_arg), expected)

    def test_average_rows(self):
        test_rows = [
            "Date,Time,Val1,Val2,Val3",
            "\n01/01/1970,00:00:00,1.0,2.0,3.0",
            "\n01/01/1970,00:00:08,2.0,2.15,3.00000007",
            "\n01/01/1970,00:00:16,5.0,2.01,3.03300000",
        ]
        self.assertEqual(
            list(utils.average_rows(iter(test_rows), 2)),
            [
                "Date,Time,Val1,Val2,Val3",
                "\n01/01/1970,00:00:00,1.5,2.075,3.00000004",
                "\n01/01/1970,00:00:16,5.0,2.01,3.033",
            ],
        )
        modified_test_rows = test_rows.copy()
        modified_test_rows[-1] = test_rows[-1].rstrip("0")
        self.assertEqual(
            list(utils.average_rows(iter(test_rows), 1)), modified_test_rows
        )
        self.assertEqual(
            list(utils.average_rows(iter(test_rows), 3, 5)),
            [
                "Date,Time,Val1,Val2,Val3",
                "\n01/01/1970,00:00:00,2.66667,2.05333,3.011",
            ],
        )

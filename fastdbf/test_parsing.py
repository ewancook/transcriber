import functools
import tempfile
import unittest
from itertools import chain, combinations

import dbf

from fastdbf import parse_float_file, parse_tag_file

float_table_format = "Date C(8); Time C(8); Mlltm N(3,0); TagIndex N(1,0); Value C(8); Internal N(1,0); Marker C(1)"
tag_table_format = (
    "Tagname C(255); TTagIndex N(5,0); TagType N(1,0); TagDataTyp N(2,0)"
)

float_rows = [
    ("19700101", "00:00:00", 100, 2, "00000000", 0, "B"),
    ("19700101", "00:00:08", 200, 2, "00000001", 0, " "),
    ("19700101", "00:00:16", 300, 2, "00000002", 0, "E"),
    ("19700101", "00:00:24", 400, 0, "00000003", 0, "B"),
    ("19700101", "00:00:24", 400, 2, "00000004", 0, "B"),
    ("19700101", "00:00:24", 400, 4, "00000005", 0, "B"),
    ("19700101", "00:00:32", 500, 0, "00000006", 0, " "),
    ("19700101", "00:00:32", 500, 2, "00000007", 0, " "),
    ("19700101", "00:00:32", 500, 4, "00000008", 0, " "),
    ("19700101", "00:00:40", 600, 0, "00000009", 0, "E"),
    ("19700101", "00:00:40", 600, 2, "00000010", 0, "E"),
    ("19700101", "00:00:40", 600, 4, "00000011", 0, "E"),
    ("19700101", "00:00:48", 700, 0, "00000012", 0, "B"),
    ("19700101", "00:00:48", 700, 1, "00000013", 0, "B"),
    ("19700101", "00:00:48", 700, 2, "00000014", 0, "B"),
    ("19700101", "00:00:48", 700, 4, "00000015", 0, "B"),
    ("19700101", "00:00:56", 800, 0, "00000016", 0, "E"),
    ("19700101", "00:00:56", 800, 1, "00000017", 0, "E"),
    ("19700101", "00:00:56", 800, 2, "00000018", 0, "E"),
    ("19700101", "00:00:56", 800, 4, "00000019", 0, "E"),
    ("19700101", "00:01:04", 900, 2, "00000020", 0, "B"),
    ("19700101", "00:01:12", 000, 2, "00000021", 0, "E"),
    ("19700101", "00:01:20", 100, 0, "00000022", 0, "B"),
    ("19700101", "00:01:28", 200, 0, "00000023", 0, "E"),
    ("19700101", "00:01:36", 300, 2, "00000024", 0, "B"),
    ("19700101", "00:01:42", 400, 2, "00000025", 0, "E"),
]

tag_rows = [
    ("First", 0, 2, 1),
    ("Second", 1, 2, 1),
    ("Third", 2, 2, 1),
    ("Fourth", 3, 2, 1),
    ("Fifth", 4, 2, 1),
    ("Sixth", 5, 2, 1),
]


def make_fields_correct_case(filename, fields):
    field_bytes = {
        bytes(field, encoding="cp437"): bytes(field.upper(), encoding="cp437")
        for field in fields
    }
    data = ""
    with open(filename, "rb") as f:
        data = f.read()
    for new, old in field_bytes.items():
        data = data.replace(old, new)
    with open(filename, "wb") as f:
        f.write(data)


def create_dbf_file(rows, data_format):
    def inner(func):
        @functools.wraps(func)
        def wraps(*args, **kwargs):
            dbf_file = tempfile.NamedTemporaryFile(delete=False)
            dbf_file.close()
            table = dbf.Table(dbf_file.name, data_format, dbf_type="db3")
            table.open(mode=dbf.READ_WRITE)
            for row in rows:
                table.append(row)
            table.close()
            kwargs["filename"] = dbf_file.name
            func(*args, **kwargs)

        return wraps

    return inner


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


class TestReadFloatFile(unittest.TestCase):
    def setUp(self):
        self.fields = [
            "Date",
            "Time",
            "Milltm",
            "TagIndex",
            "Value",
            "Internal",
            "Marker",
        ]
        self.tags = [0, 1, 2, 3, 4]

    @create_dbf_file(float_rows, float_table_format)
    def test_read_all(self, **kwargs):
        filename = kwargs["filename"]
        make_fields_correct_case(filename, self.fields)
        for tags in powerset(self.tags):
            rows = parse_float_file(filename, tags)
            expected = [r[4] for r in float_rows if r[3] in tags]
            for row, result in zip(rows, expected):
                self.assertEqual(row["Value"].decode("utf8"), result)


class TestReadTagFile(unittest.TestCase):
    def setUp(self):
        self.fields = ["Tagname", "TTagIndex", "TagType", "TagDataTyp"]

    @create_dbf_file(tag_rows, tag_table_format)
    def test_read_tag_file(self, **kwargs):
        filename = kwargs["filename"]
        make_fields_correct_case(filename, self.fields)
        for row, result in zip(tag_rows, parse_tag_file(filename)):
            res = int(result["TTagIndex"].decode("utf-8"))
            self.assertEqual(row[1], res)

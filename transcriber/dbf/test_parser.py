import functools
import random
import string
import tempfile
import unittest
from itertools import chain, combinations

import dbf

from transcriber.dbf.parser import Parser


def generate_parsed_pairs(rows, parsed, fields, lookup=None):
    for expected, actual in zip(rows, parsed):
        for i, field_name in enumerate(fields):
            if lookup is not None and i not in lookup:
                continue
            expected_value = expected[i]
            if isinstance(expected_value, int):
                yield (expected[i], int(actual[field_name]))
            else:
                yield (expected[i].encode("ascii"), actual[field_name])


def generate_random_string():
    return "".join(random.choice(string.ascii_letters) for i in range(8))


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


dbf_rows = [
    ("19700101", "00:00:00", 100, 0, generate_random_string(), 0),
    ("19700101", "00:00:00", 100, 1, generate_random_string(), 0),
    ("19700101", "00:00:00", 100, 2, generate_random_string(), 0),
    ("19700101", "00:00:00", 100, 3, generate_random_string(), 0),
    ("19700101", "00:00:00", 100, 4, generate_random_string(), 0),
    ("19700101", "00:00:08", 200, 0, generate_random_string(), 0),
    ("19700101", "00:00:08", 200, 1, generate_random_string(), 0),
    ("19700101", "00:00:08", 200, 2, generate_random_string(), 0),
    ("19700101", "00:00:08", 200, 3, generate_random_string(), 0),
    ("19700101", "00:00:08", 200, 4, generate_random_string(), 0),
    ("19700101", "00:00:16", 300, 0, generate_random_string(), 0),
    ("19700101", "00:00:16", 300, 1, generate_random_string(), 0),
    ("19700101", "00:00:16", 300, 2, generate_random_string(), 0),
    ("19700101", "00:00:16", 300, 3, generate_random_string(), 0),
    ("19700101", "00:00:16", 300, 4, generate_random_string(), 0),
]

dbf_table_format = "Date C(8); Time C(8); Mlltm N(3,0); TagIndex N(1,0); Value C(8); Internal N(1,0)"


def create_dbf_file(func):
    @functools.wraps(func)
    def wraps(*args, **kwargs):
        dbf_file = tempfile.NamedTemporaryFile(delete=False)
        dbf_file.close()
        table = dbf.Table(dbf_file.name, dbf_table_format, dbf_type="db3")
        table.open(mode=dbf.READ_WRITE)
        for row in dbf_rows:
            table.append(row)
        table.close()
        kwargs["dbf_filename"] = dbf_file.name
        func(*args, **kwargs)
    return wraps


class TestParser(unittest.TestCase):
    def setUp(self):
        self.all_fields = [
            "DATE",
            "TIME",
            "MLLTM",
            "TAGINDEX",
            "VALUE",
            "INTERNAL",
        ]
        self.all_tags = [0, 1, 2, 3, 4, 5]

    @create_dbf_file
    def test_parse_all(self, **kwargs):
        dbf_filename = kwargs["dbf_filename"]
        parser = Parser(required_fields=self.all_fields)
        parsed = parser.parse_all(dbf_filename)
        for expected, actual in generate_parsed_pairs(
            dbf_rows, parsed, self.all_fields
        ):
            self.assertEqual(expected, actual)

    @create_dbf_file
    def test_parse_selection_on_every_tag_combination(self, **kwargs):
        dbf_filename = kwargs["dbf_filename"]
        required_fields = ["DATE", "TIME", "TAGINDEX", "VALUE"]
        for required_tags in powerset(self.all_tags):
            parser = Parser(
                required_fields=required_fields,
                required_tags=required_tags,
                all_tags=self.all_tags,
            )
            lookup = set([self.all_fields.index(f) for f in required_fields])
            parsed = parser.parse_selection(dbf_filename)

            rows = [
                row
                for i, row in enumerate(dbf_rows)
                if i % len(self.all_tags) in required_tags
            ]
            for expected, actual in generate_parsed_pairs(
                rows, parsed, self.all_fields, lookup
            ):
                self.assertEqual(expected, actual)

    @create_dbf_file
    def test_parse_all_on_every_field_combination_backwards(self, **kwargs):
        dbf_filename = kwargs["dbf_filename"]
        for required_fields in powerset(self.all_fields[::-1]):
            parser = Parser(required_fields=required_fields,)
            lookup = set([self.all_fields.index(f) for f in required_fields])
            parsed = parser.parse_all(dbf_filename)
            for expected, actual in generate_parsed_pairs(
                dbf_rows, parsed, self.all_fields, lookup
            ):
                self.assertEqual(expected, actual)

from itertools import islice
from struct import Struct

from transcriber.converter import utils

from transcriber.dbf.parser import Parser

from PyQt5 import QtCore


def _format_date(date):
    day, month, year = date[6:], date[4:6], date[:4]
    return f"{day}/{month}/{year}"


def create_worker(filename, tags, total_tags, tag_lookup):
    return DBFConverterWorker(filename, tags, total_tags, tag_lookup)


class DBFConverterWorker(utils.ConverterWorker):
    def __init__(self, *args, **kwargs):
        super(DBFConverterWorker, self).__init__(*args, **kwargs)
        self.parser = Parser(["Date", "Time", "Value"])

    def convert(self):
        table = self.parser.parse_file(self.filename)
        double_struct = Struct("<d")

        lines = set([self.tag_lookup.index(t) for t in self.tags])
        total_tags = self.total_tags

        with open(utils.transcribed_filename(self.filename), "w") as out:
            out.write(",".join(["Date", "Time", *[self.tag_lookup[l] for l in lines]]))
            tags_written = num_tags = len(lines)
            for i, row in enumerate(table, total_tags):
                if i % total_tags not in lines:
                    continue
                value = round(double_struct.unpack(row["Value"])[0], 8)
                if tags_written == num_tags:
                    date = _format_date(row["Date"].decode())
                    time = row["Time"].decode()
                    out.write(f"\n{date},{time},{value}")
                    tags_written = 1
                else:
                    out.write(f",{value}")
                    tags_written += 1

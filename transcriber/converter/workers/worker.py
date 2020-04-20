from itertools import islice
from struct import Struct

from transcriber.converter.workers import utils
from transcriber.dbf.parser import Parser


class CSVWorker:
    def __init__(self, filename, tags, tag_lookup):
        self.filename = filename
        self.tags = tags
        self.tag_lookup = tag_lookup
        self.total_tags = len(self.tag_lookup)

    def work(self):
        self.convert()
        return self.filename

    def convert(self):
        with open(self.filename) as file:
            lines = sorted([self.tag_lookup.index(t) for t in self.tags])
            lines_set = set(lines)

            total_tags = self.total_tags

            with open(utils.transcribed_filename(self.filename), "w") as out:
                tags_written = num_tags = len(lines)
                out.write(
                    ",".join(
                        ["Date", "Time", *[self.tag_lookup[i] for i in lines]]
                    )
                )
                for i, line in enumerate(islice(file, 1, None)):
                    if i % total_tags not in lines_set:
                        continue
                    if tags_written == num_tags:
                        date, time, _, val = utils.data_from_line(line)
                        out.write(f"\n{date},{time},{val}")
                        tags_written = 1
                    else:
                        out.write(f",{utils.val_from_line(line)}")
                        tags_written += 1


class DBFWorker(CSVWorker):
    def __init__(self, filename, tags, tag_lookup):
        super(DBFWorker, self).__init__(filename, tags, tag_lookup)
        self.parser = Parser(
            required_fields=["Date", "Time", "Value"],
            required_tags=[self.tag_lookup.index(t) for t in self.tags],
            total_tags=self.total_tags,
        )

    def convert(self):
        table = self.parser.parse_selection(self.filename)
        double_struct = Struct("<d")

        lines = sorted([self.tag_lookup.index(t) for t in self.tags])

        with open(utils.transcribed_filename(self.filename), "w") as out:
            out.write(
                ",".join(
                    ["Date", "Time", *[self.tag_lookup[l] for l in lines]]
                )
            )
            tags_written = num_tags = len(lines)
            for row in table:
                value = round(double_struct.unpack(row["Value"])[0], 8)
                if tags_written == num_tags:
                    date = utils.format_dbf_date(row["Date"].decode())
                    time = row["Time"].decode()
                    out.write(f"\n{date},{time},{value}")
                    tags_written = 1
                else:
                    out.write(f",{value}")
                    tags_written += 1

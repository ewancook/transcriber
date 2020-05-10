from struct import Struct

from transcriber.converter.dbfworker import utils
from transcriber.dbf.parser import Parser


def write_csv(csv_file, csv_data):
    csv_file.write("".join(csv_data))


class Worker:
    def __init__(self, filename, tags, tag_lookup, total_tags=0):
        self.filename = filename
        self.tags = tags
        self.tag_lookup = tag_lookup
        self.total_tags = total_tags if total_tags else len(tag_lookup)

    def work(self):
        try:
            self.convert()
            return self.filename
        except Exception as error:
            raise Exception(self.filename, error)


class DBFWorker(Worker):
    def __init__(self, filename, tags, tag_lookup, total_tags=0):
        super(DBFWorker, self).__init__(filename, tags, tag_lookup, total_tags)
        self.parser = Parser(required_fields=["Date", "Time", "Value"])
        self.required_tag_indices = [
            self.tag_lookup.index(t) for t in self.tags
        ]
        self.total_tags = total_tags if total_tags else len(tag_lookup)

    def _parse_selection(self, filename):
        return self.parser.parse_selection(
            filename, self.required_tag_indices, self.total_tags
        )

    def convert(self):
        table = self._parse_selection(self.filename)
        with open(utils.transcribed_filename(self.filename), "w") as csv_file:
            write_csv(csv_file, self.generate_csv(table))

    def generate_csv(self, table):
        lines = sorted([self.tag_lookup.index(t) for t in self.tags])
        double_struct = Struct("<d")
        unpack = double_struct.unpack

        yield ",".join(["Date", "Time", *[self.tag_lookup[l] for l in lines]])

        tags_written = num_tags = len(lines)
        for row in table:
            value = round(unpack(row["Value"])[0], 8)
            if tags_written == num_tags:
                date = utils.format_dbf_date(row["Date"].decode())
                time = row["Time"].decode()
                yield f"\n{date},{time},{value}"
                tags_written = 1
            else:
                yield f",{value}"
                tags_written += 1

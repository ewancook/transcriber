from transcriber.converter.dbfworker import utils
from transcriber.dbf.parser import Parser


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
            utils.write_csv(
                csv_file, utils.generate_csv(table, self.tags, self.tag_lookup)
            )

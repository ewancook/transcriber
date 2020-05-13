from transcriber.converter.dbfworker import utils
from transcriber.dbf.parser import Parser

DEFAULT_DECIMAL_PLACES = 8


class Worker:
    def __init__(self, **kwargs):
        self.decimal_places = DEFAULT_DECIMAL_PLACES
        self.rows_to_average = None
        for name, value in kwargs.items():
            setattr(self, name, value)
        if getattr(self, "total_tags", None) is None:
            self.total_tags = len(self.tag_lookup)

    def work(self):
        try:
            self.convert()
            return self.filename
        except Exception as error:
            raise Exception(self.filename, error)


class DBFWorker(Worker):
    def __init__(self, **kwargs):
        super(DBFWorker, self).__init__(**kwargs)
        self.parser = Parser(required_fields=["Date", "Time", "Value"])
        self.required_tag_indices = [
            self.tag_lookup.index(t) for t in self.tags
        ]

    def _parse_selection(self, filename):
        return self.parser.parse_selection(
            filename, self.required_tag_indices, self.total_tags
        )

    def convert(self):
        table = self._parse_selection(self.filename)
        csv_contents = utils.generate_csv(
            table, self.tags, self.tag_lookup, self.decimal_places
        )
        with open(utils.transcribed_filename(self.filename), "w") as csv_file:
            utils.write_csv(
                csv_file,
                csv_contents
                if self.rows_to_average is None
                else utils.average_rows(
                    csv_contents, self.rows_to_average, self.decimal_places
                ),
            )

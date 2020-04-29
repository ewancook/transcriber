import mmap

from dbfread import DBF


def create_row_skip_sequence(required, total, row_length):
    sequence = []
    for item in total:
        if item in required:
            sequence.extend([(True, row_length - 1), [False, 1]])
        elif len(sequence) and not sequence[-1][0]:
            sequence[-1][1] += row_length
        else:
            sequence.append([False, row_length])
    if not sequence[-1][0]:
        sequence[-1][1] -= 1
        if not sequence[-1][1]:
            sequence.pop()
    return sequence


def create_field_skip_sequence(required, total):
    sequence = []
    for item in total:
        if item.name in required:
            sequence.append((item.name, item.length))
        elif len(sequence) and not sequence[-1][0]:
            sequence[-1][1] += item.length
        else:
            sequence.append([False, item.length])
    return sequence


class SubclassedDBF(DBF):
    def __init__(self, filename, tags, **kwargs):
        super(SubclassedDBF, self).__init__(filename)
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.required_fields = tags

    def _iter_records_no_row_skipping(self, record_type=b" "):
        with open(self.filename, "rb") as _infile:
            infile = mmap.mmap(_infile.fileno(), 0, access=mmap.ACCESS_READ)

            skip_record = self._skip_record
            read = infile.read
            seek = infile.seek

            seek(self.header.headerlen, 0)

            field_skip_sequence = create_field_skip_sequence(
                self.required_fields, self.fields
            )

            line_values = {}
            clear_line_values = line_values.clear
            while True:
                sep = read(1)
                if sep == record_type:
                    clear_line_values()
                    for name, length in field_skip_sequence:
                        if name:
                            line_values[name] = read(length)
                        else:
                            seek(length, 1)
                    yield line_values
                elif sep in (b"\x1a", b""):
                    break
                else:
                    skip_record(infile)
            infile.close()

    def _iter_records(self, record_type=b" "):
        with open(self.filename, "rb") as _infile:
            infile = mmap.mmap(_infile.fileno(), 0, access=mmap.ACCESS_READ)

            skip_record = self._skip_record
            read = infile.read
            seek = infile.seek

            seek(self.header.headerlen, 0)

            field_skip_sequence = create_field_skip_sequence(
                self.required_fields, self.fields
            )
            row_skip_sequence = create_row_skip_sequence(
                self.required_tags,
                range(len(self.all_tags)),
                self.header.recordlen,
            )

            line_values = {}
            clear_line_values = line_values.clear
            while True:
                sep = read(1)
                if sep == record_type:
                    for read_row, length in row_skip_sequence:
                        if not read_row:
                            seek(length, 1)
                        else:
                            clear_line_values()
                            for name, length in field_skip_sequence:
                                if not name:
                                    seek(length, 1)
                                else:
                                    line_values[name] = read(length)
                            yield line_values
                elif sep in (b"\x1a", b""):
                    break
                else:
                    skip_record(infile)
            infile.close()

    def __len__(self):
        # TODO: why was this called (& slowing everything down)?
        return 0


class Parser:
    def __init__(
        self, required_fields, encoding="cp437", required_tags=[], all_tags=[],
    ):
        self.required_fields = set(required_fields)
        self.encoding = encoding
        self.required_tags = set(required_tags)
        self.all_tags = all_tags

    @property
    def tags(self):
        return self.required_fields

    @tags.setter
    def set_tags(self, required_fields):
        self.required_fields = set(required_fields)

    def parse_all(self, filename):
        return SubclassedDBF(
            filename,
            self.required_fields,
            encoding=self.encoding,
            recfactory=None,
            raw=True,
        )._iter_records_no_row_skipping()

    def parse_selection(self, filename):
        return SubclassedDBF(
            filename,
            self.required_fields,
            required_tags=self.required_tags,
            all_tags=self.all_tags,
            encoding=self.encoding,
            recfactory=None,
            raw=True,
        )

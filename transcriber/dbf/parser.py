from dbfread import DBF


def create_skip_sequence(selected_fields, fields):
    sequence = []
    for field in fields:
        if field.name in selected_fields:
            sequence.append((field.name, field.length))
            continue
        elif len(sequence) and not sequence[-1][0]:
            sequence[-1][1] += field.length
        else:
            sequence.append([False, field.length])
    return sequence


class SubclassedDBF(DBF):
    def __init__(self, filename, tags, **kwargs):
        super(SubclassedDBF, self).__init__(filename)
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.required_tags = tags

    def _iter_records(self, record_type=b" "):
        with open(self.filename, "rb") as infile:
            infile.seek(self.header.headerlen, 0)

            skip_record = self._skip_record
            read = infile.read
            seek = infile.seek

            skip_sequence = create_skip_sequence(
                self.required_tags, self.fields)

            while True:
                sep = read(1)
                if sep == record_type:
                    line_values = {}
                    for name, length in skip_sequence:
                        if not name:
                            seek(length, 1)
                        else:
                            line_values[name] = read(length)
                    yield line_values
                elif sep in (b"\x1a", b""):
                    break
                else:
                    skip_record(infile)


class Parser:
    def __init__(self, required_tags, encoding="cp437"):
        self.required_tags = set(required_tags)
        self.encoding = encoding

    @property
    def tags(self):
        return self.required_tags

    @tags.setter
    def set_tags(self, required_tags):
        self.required_tags = set(required_tags)

    def parse_file(self, filename):
        return SubclassedDBF(filename, self.required_tags,
                             encoding=self.encoding, recfactory=None, raw=True)

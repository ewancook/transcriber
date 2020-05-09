import mmap

from dbfread import DBF

from transcriber.dbf.utils import (
    create_field_skip_sequence,
    create_row_skip_sequence,
)


class SubclassedDBF(DBF):
    def __init__(self, filename, required_fields, **kwargs):
        super(SubclassedDBF, self).__init__(filename)
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.required_fields = required_fields

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
                self.required_tag_indices,
                range(self.total_tags),
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
    def __init__(self, required_fields, encoding="cp437"):
        if not isinstance(required_fields, set):
            required_fields = set(required_fields)
        self.required_fields = required_fields
        self.encoding = encoding

    @property
    def tags(self):
        return self.required_fields

    def parse_all(self, filename):
        return SubclassedDBF(
            filename,
            self.required_fields,
            encoding=self.encoding,
            recfactory=None,
        )._iter_records_no_row_skipping()

    def parse_selection(self, filename, required_tag_indices, total_tags):
        if not isinstance(required_tag_indices, set):
            required_tag_indices = set(required_tag_indices)
        return SubclassedDBF(
            filename,
            self.required_fields,
            required_tag_indices=required_tag_indices,
            total_tags=total_tags,
            encoding=self.encoding,
            recfactory=None,
        )

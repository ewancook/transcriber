import mmap
from itertools import islice, takewhile

from dbfread import DBF
from transcriber.dbf.utils import (
    create_field_skip_sequence,
    create_row_skip_sequence,
)

MARKER = "Marker"


class SubclassedDBF(DBF):
    def __init__(self, filename, **kwargs):
        super(SubclassedDBF, self).__init__(filename)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _iter_records_no_row_skipping(self, required_fields, record_type=b" "):
        with open(self.filename, "rb") as _infile:
            infile = mmap.mmap(_infile.fileno(), 0, access=mmap.ACCESS_READ)
            infile.seek(self.header.headerlen, 0)

            field_skip_sequence = create_field_skip_sequence(
                required_fields, self.fields
            )
            yield from self._read_rows_no_skipping(field_skip_sequence, infile)
            infile.close()

    def _read_rows_no_skipping(
        self, field_skip_sequence, infile, record_type=b" "
    ):
        line_values = {}
        clear_line_values = line_values.clear

        skip_record = self._skip_record
        read = infile.read

        row_length = self.header.recordlen - 1
        while True:
            sep = read(1)
            if sep == record_type:
                clear_line_values()
                row = read(row_length)
                for name, start, end in field_skip_sequence:
                    if name:
                        line_values[name] = row[start:end]
                yield line_values
            elif sep in (b"\x1a", b""):
                break
            else:
                skip_record(infile)

    def parse_float_file(
        self, required_fields, required_tag_indices, record_type=b" "
    ):
        with open(self.filename, "rb") as _infile:
            infile = mmap.mmap(_infile.fileno(), 0, access=mmap.ACCESS_READ)
            infile.seek(self.header.headerlen, 0)
            field_skip_sequence = create_field_skip_sequence(
                required_fields, self.fields
            )
            print([(f.name, f.length) for f in self.fields])
            yield from self._read_float_file(
                field_skip_sequence, infile, required_tag_indices
            )
            infile.close()

    def _read_float_file(
        self, field_skip_sequence, infile, required_tag_indices
    ):
        total_tags = 0
        # start_pos = infile.tell()
        for i, row in enumerate(
            self._read_rows_no_skipping(field_skip_sequence, infile)
        ):
            if row[MARKER] != b"B":
                total_tags = i
                break
            # print(i, required_tag_indices)
            if i in required_tag_indices:
                yield row
        # print(f"total tags: {total_tags}")
        # total_tags += 1
        # infile.seek(start_pos)
        row_skip_sequence = create_row_skip_sequence(
            required_tag_indices, range(total_tags), self.header.recordlen,
        )
        later_rows = self._read_rows_with_skipping(
            row_skip_sequence, field_skip_sequence, infile
        )
        tags_per_section = len(required_tag_indices)
        first_row = {}
        try:
            while True:
                rows = islice(later_rows, tags_per_section)
                first_row = next(rows)
                yield first_row
                yield from rows
                if first_row[MARKER] == b"E":
                    break
        except StopIteration:
            return None
        expected_pos = (
            self.header.numrecords * self.header.recordlen
            + self.header.headerlen
        )
        if infile.tell() - expected_pos not in [0, 1]:
            yield from self._read_rows_no_skipping(field_skip_sequence, infile)

    def _read_rows_with_skipping(
        self, row_skip_sequence, field_skip_sequence, infile, record_type=b" "
    ):
        line_values = {}
        clear_line_values = line_values.clear

        skip_record = self._skip_record
        read = infile.read
        seek = infile.seek

        row_length = self.header.recordlen - 1
        while True:
            sep = read(1)
            if sep == record_type:
                for read_row, length in row_skip_sequence:
                    if not read_row:
                        seek(length, 1)
                    else:
                        clear_line_values()
                        row = read(row_length)
                        for name, start, end in field_skip_sequence:
                            if name:
                                line_values[name] = row[start:end]
                        yield line_values
            elif sep in (b"\x1a", b""):
                break
            else:
                skip_record(infile)

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
            filename, encoding=self.encoding, recfactory=None,
        )._iter_records_no_row_skipping(self.required_fields)

    def parse_float_file(self, filename, required_tag_indices):
        if not isinstance(required_tag_indices, set):
            required_tag_indices = set(required_tag_indices)
        return SubclassedDBF(
            filename,
            required_tag_indices=required_tag_indices,
            encoding=self.encoding,
            recfactory=None,
        ).parse_float_file(self.required_fields, required_tag_indices)

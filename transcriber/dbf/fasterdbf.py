import mmap

import dbfread
from transcriber.dbf import utils


class FasterDBF(dbfread.DBF):
    def __init__(self, filename, encoding="cp437", recfactory=None, **kwargs):
        super(FasterDBF, self).__init__(
            filename, encoding=encoding, recfactory=recfactory, **kwargs
        )

        self.encoding = encoding
        self.recfactory = recfactory
        for k, v in kwargs.items():
            setattr(self, k, v)

    def parse_float_file(self, _infile, required_indices, record_type=b" "):
        with open(self.filename, "rb") as _infile:
            infile = mmap.mmap(_infile.fileno(), 0, access=mmap.ACCESS_READ)
            infile.seek(self.header.headerlen, 0)
            yield from utils.read_float_file(
                infile, required_indices, self.header.recordlen, self.fields
            )
            infile.close()

    def parse_tag_file(self, record_type=b" "):
        with open(self.filename, "rb") as _infile:
            infile = mmap.mmap(_infile.fileno(), 0, access=mmap.ACCESS_READ)
            infile.seek(self.header.headerlen, 0)
            field_seq = utils.tag_field_parsing_sequence(self.fields)
            record_length = self.header.recordlen
            yield from utils.read_rows_without_row_skipping(
                infile, field_seq, record_length
            )
            infile.close()

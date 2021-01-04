import mmap

from transcriber.dbf import fasterdbf


class Parser:
    def __init__(self, encoding="cp437"):
        self.encoding = encoding

    def parse_float_file(self, filename, required_indices):
        if not isinstance(required_indices, set):
            required_indices = set(required_indices)
        parser = fasterdbf.FasterDBF(filename, self.encoding)
        with open(filename, "rb") as infile:
            return parser.parse_float_file(infile, required_indices)

    def parse_tag_file(self, filename):
        parser = fasterdbf.FasterDBF(filename, self.encoding)
        return parser.parse_tag_file(filename)

from itertools import islice

from transcriber.dbf.parser import Parser

from PyQt5 import QtWidgets


class TagSelecterModel:
    def __init__(self):
        self.tags = []
        self.parser = Parser(["Tagname"])

    def load(self, filename, encoding="utf-8"):
        self.tags = [r["Tagname"].decode(encoding).strip()
                     for r in self.parser.parse_file(filename)]

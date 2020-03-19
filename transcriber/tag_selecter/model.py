from itertools import islice

from PyQt5 import QtWidgets


class TagSelecterModel:
    def __init__(self):
        self.tags = []

    def load(self, filename):
        with open(filename) as f:
            try:
                self.tags = [l.split(",")[0].strip()
                             for l in islice(f, 1, None)]
            except BaseException:
                pass

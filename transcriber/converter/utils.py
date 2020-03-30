from itertools import islice

from PyQt5 import QtCore


def data_from_line(line):
    date, time, _, tag, val = line.split(",")[:5]
    return flip_date(date), time, tag.strip(), val.strip()


def flip_date(date):
    month, day, year = date.split("/")
    return f"{day}/{month}/{year}"


def val_from_line(line):
    return line.split(",")[4].strip()


def create_worker(filename, tags, total_tags):
    return ConverterWorker(filename, tags, total_tags)


def transcribed_filename(filename):
    name = filename.rsplit(".")[0]
    return f"{name} (Transcribed).csv"


class ConverterWorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(Exception)


class ConverterWorker(QtCore.QRunnable):
    def __init__(self, *args, **kwargs):
        super(ConverterWorker, self).__init__()
        self.filename, self.tags, self.total_tags = args
        self.signals = ConverterWorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        try:
            self.convert()
        except Exception as e:
            self.signals.error.emit(e)
        self.signals.finished.emit()

    def connect_finished(self, slot):
        self.signals.finished.connect(slot, QtCore.Qt.DirectConnection)

    def disconnect_finished(self, slot):
        self.signals.finished.disconnect(slot)

    def connect_error(self, slot):
        self.signals.error.connect(slot, QtCore.Qt.DirectConnection)

    def disconnect_error(self, slot):
        self.signals.error.disconnect(slot)

    def convert(self):
        with open(self.filename) as file:
            lines = set()
            values, ordered_tags = [], []
            for i, line in enumerate(islice(file, 1, self.total_tags + 1)):
                date, time, tag, val = data_from_line(line)
                if tag in self.tags:
                    lines.add(i)
                    ordered_tags.append(tag)
                    values.append(val)
            with open(transcribed_filename(self.filename), "w") as out:
                print(",".join(["Date", "Time", *ordered_tags]), file=out)
                out.write(",".join([date, time, *values]))
                self.transpose(file, out, lines)

    def transpose(self, read_file, out_file, lines):
        tags_written = num_tags = len(lines)
        for i, line in enumerate(read_file):
            if i % self.total_tags not in lines:
                continue
            if tags_written == num_tags:
                date, time, _, val = data_from_line(line)
                out_file.write(f"\n{date},{time},{val}")
                tags_written = 1
            else:
                out_file.write(f",{val_from_line(line)}")
                tags_written += 1

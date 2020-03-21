from itertools import islice

from PyQt5 import QtCore


def data_from_line(line):
    date, time, _, tag, val = line.split(",")[:5]
    return date, time, tag.strip(), val.strip()


def flip_date(date):
    month, day, year = date.split("/")
    return "{}/{}/{}".format(day, month, year)


def create_worker(filename, tags, total_tags):
    return ConverterWorker(filename, tags, total_tags)


def transcribed_filename(filename):
    return "{} (Transcribed).csv".format(filename.rsplit(".")[0])


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
        with open(self.filename) as f:
            order, vals = [], []
            date, time = "", ""
            for line in islice(f, 1, self.total_tags + 1):
                date, time, tag, val = data_from_line(line)
                if tag in self.tags:
                    order.append(tag)
                    vals.append(val)
            first_data = "{},{},{}".format(
                flip_date(date), time, ",".join(vals))
            with open(transcribed_filename(self.filename), "w") as out:
                self.transpose(f, order, out, first_data)

    def transpose(self, file, tags, out, first_data):
        print("Date,Time,{}".format(",".join(tags)), file=out)
        out.write(first_data)
        tags_written = num_tags = len(tags)
        for line in islice(file, 1, None):
            date, time, tag, val = data_from_line(line)
            if tag not in tags:
                continue
            if tags_written == num_tags:
                out.write("\n{},{},{}".format(flip_date(date), time, val))
                tags_written = 1
            else:
                out.write(",{}".format(val))
                tags_written += 1

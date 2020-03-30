from PyQt5 import QtCore

from . import utils, model


class MultiThreadingConverterModel(model.ConverterModel):
    def __init__(self):
        super(MultiThreadingConverterModel, self).__init__()
        self.pool = QtCore.QThreadPool()

    @QtCore.pyqtSlot(list, set, int, int)
    def convert(self, filenames, tags, total_tags, num_cpu):
        self.total_files = len(filenames)
        self.conversion_started.emit()
        self.pool.setMaxThreadCount(num_cpu)
        for filename in filenames:
            worker = utils.create_worker(filename, tags, total_tags)
            worker.connect_finished(self.update_conversion_total)
            worker.connect_error(self.conversion_error.emit)
            self.pool.start(worker)
        self.pool.waitForDone()
        self.conversion_finished.emit()

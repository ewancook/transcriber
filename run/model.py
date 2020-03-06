from itertools import islice

from PyQt5 import QtCore

class RunModel:
    def __init__(self):
        pass

    def convert(self, filename, tags):
        with open(filename) as f:
            out_name = "{} (Slim).csv".format(filename.rsplit(".")[0])
            with open(out_name, "w") as out:
                print("Date,Time,Tag,Value", file=out)
                for line in islice(f, 1, None):
                    date, time, _, tag, val = line.split(",")[:5]
                    tag = tag.strip()
                    if tag not in tags:
                        continue
                    print("{},{},{},{}".format(date, time, tag, float(val)), file=out)

    def connect_slim_progress(self, slot):
        self.progress.connect(slot)

    def disconnect_slim_progress(self, slot):
        self.progress.disconnect(slot)

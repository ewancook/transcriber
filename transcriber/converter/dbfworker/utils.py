from itertools import islice
from struct import Struct

VALUE = "Value"
DATE = "Date"
TIME = "Time"


def data_from_line(line):
    date, time, _, tag, val = line.split(",")[:5]
    return flip_date(date), time, tag.strip(), val.strip()


def flip_date(date):
    month, day, year = date.split("/")
    return f"{day}/{month}/{year}"


def val_from_line(line):
    return line.split(",")[4].strip()


def transcribed_filename(filename):
    name = filename.rsplit(".", 1)[0]
    return f"{name} (Transcribed).csv"


def format_dbf_date(date):
    day, month, year = date[6:], date[4:6], date[:4]
    return f"{day}/{month}/{year}"


def write_csv(csv_file, csv_data):
    csv_file.write("".join(csv_data))


def _mean(gen, decimal_places):
    n = 0
    p = 10 ** decimal_places
    mean = 0.0
    for i in gen:
        n += 1
        mean += (i - mean) / n
    return int(mean * p + 0.5) / p if n else 0


def average_rows(table, n_rows, decimal_places):
    yield next(table)
    try:
        while True:
            rows = (r.lstrip("\n").split(",") for r in islice(table, n_rows))
            columns = zip(*rows)
            date = next(columns)[0]
            time = next(columns)[0]
            averaged_values = (
                str(_mean((float(i) for i in c), decimal_places))
                for c in columns
            )
            yield f"\n{date},{time},{','.join(averaged_values)}"
    except StopIteration:
        return


def generate_csv(table, tags, tag_lookup, decimal_places):
    table = iter(table)
    lines = sorted([tag_lookup.index(t) for t in tags])
    double_struct = Struct("<d")
    unpack = double_struct.unpack
    num_tags = len(lines)
    precision = 10 ** decimal_places

    yield ",".join([DATE, TIME, *[tag_lookup[l] for l in lines]])

    try:
        while True:
            rows = islice(table, num_tags)
            first_column = next(rows)
            date = format_dbf_date(first_column[DATE].decode())
            time = first_column[TIME].decode()
            value = (
                int(unpack(first_column[VALUE])[0] * precision + 0.5)
                / precision
            )
            values = [
                str(int(unpack(row[VALUE])[0] * precision + 0.5) / precision)
                for row in rows
            ]
            if not len(values):
                yield f"\n{date},{time},{value}"
            else:
                yield f"\n{date},{time},{value},{','.join(values)}"
    except StopIteration:
        return

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

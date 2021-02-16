from itertools import islice

from fastdbf import parsing_sequences as ps


def read_rows_without_row_skipping(infile, field_skip_seq, record_length):
    line_values = {}
    clear_line_values = line_values.clear

    seek = infile.seek
    read = infile.read

    row_length = record_length - 1
    while True:
        sep = read(1)
        if sep == b" ":
            clear_line_values()
            row = read(row_length)
            for name, start, end in field_skip_seq:
                if name:
                    line_values[name] = row[start:end]
            yield line_values
        elif sep in (b"\x1a", b""):
            break
        else:
            seek(row_length, 1)


def read_rows_with_row_skipping(infile, row_skip_seq, record_length):
    read = infile.read
    seek = infile.seek

    row_length = record_length - 1
    chunk_values = []
    clear_chunk_values = chunk_values.clear
    while True:
        sep = read(1)
        if sep == b" ":
            clear_chunk_values()
            for read_row, length, field_seq in row_skip_seq:
                if not read_row:
                    seek(length, 1)
                else:
                    line_values = {}
                    row = read(row_length)
                    for name, start, end in field_seq:
                        if name:
                            line_values[name] = row[start:end]
                    chunk_values.append(line_values)
            yield from chunk_values
        elif sep in (b"\x1a", b""):
            break
        else:
            seek(row_length, 1)


def read_float_file(infile, required_tags, record_length, fields):
    field_seq = ps.float_field_parsing_sequence_counting(fields)
    rows = read_rows_without_row_skipping(infile, field_seq, record_length)
    tags = []

    # count tags by parsing every row
    for row in rows:
        if row["Marker"] != b"B":
            infile.seek(-record_length, 1)
            break
        tag = int(row["TagIndex"])
        tags.append(tag)
        if tag in required_tags:
            yield row
    if not tags:
        return

    parsable_tags = required_tags & set(tags)
    tags_to_parse = [tags[-1]] if not parsable_tags else parsable_tags
    row_seq = ps.float_row_parsing_sequence(
        record_length, tags_to_parse, tags, fields
    )
    rows = read_rows_with_row_skipping(infile, row_seq, record_length)

    if not parsable_tags:
        # read last row of every chunk to find 'E'
        for row in rows:
            if row["Marker"] == b"E":
                break
    else:
        first_row = {}
        chunk_size = len(parsable_tags)
        marker = False
        while True:
            chunk_rows = islice(rows, chunk_size)
            first_row = next(chunk_rows)
            marker = first_row["Marker"] == b"E"

            yield first_row
            yield from chunk_rows
            if marker:
                break
    yield from read_float_file(infile, required_tags, record_length, fields)

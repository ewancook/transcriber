import mmap
from itertools import islice


def _field_parsing_sequence(required_field_names, all_fields):
    """
    Creates a sequence for parsing fields in float files.

    :param required_field_names: all required field names to parse
    :type required_field_names: list[str]
    :param all_fields: all fields present in the dbf file
    :type all_fields: list[dbfread.field]
    """
    sequence = []
    total_length = 0
    for item in all_fields:
        if item.name in required_field_names:
            sequence.append(
                (item.name, total_length, total_length + item.length)
            )
        elif len(sequence) and not sequence[-1][0]:
            sequence[-1][2] += item.length
        else:
            sequence.append([False, total_length, total_length + item.length])
        total_length += item.length
    return sequence


def float_field_parsing_sequence_first_row(all_fields):
    required_field_names = ["Date", "Time", "Value", "Marker"]
    return _field_parsing_sequence(required_field_names, all_fields)


def float_field_parsing_sequence_later_rows(all_fields):
    required_field_names = ["Value"]
    return _field_parsing_sequence(required_field_names, all_fields)


def float_field_parsing_sequence_counting(all_fields):
    required_field_names = ["Date", "Time", "Value", "TagIndex", "Marker"]
    return _field_parsing_sequence(required_field_names, all_fields)


def tag_field_parsing_sequence(all_fields):
    required_field_names = ["Tagname", "TTagIndex"]
    return _field_parsing_sequence(required_field_names, all_fields)


def float_row_parsing_sequence(
    row_length, required_rows, all_rows, all_fields
):
    sequence = []
    first = True
    field_sequence_first_row = float_field_parsing_sequence_first_row(
        all_fields
    )
    field_sequence_later_rows = float_field_parsing_sequence_later_rows(
        all_fields
    )
    for row in all_rows:
        if row in required_rows:
            if first:
                sequence.extend(
                    [
                        (True, row_length - 1, field_sequence_first_row),
                        [False, 1, None],
                    ]
                )
                first = False
            else:
                sequence.extend(
                    [
                        (True, row_length - 1, field_sequence_later_rows),
                        [False, 1, None],
                    ]
                )
        elif len(sequence) and not sequence[-1][0]:
            sequence[-1][1] += row_length
        else:
            sequence.append([False, row_length, None])
    if not sequence[-1][0]:
        sequence[-1][1] -= 1
        if not sequence[-1][1]:
            sequence.pop()
    return sequence


def read_rows_without_row_skipping(
    infile, field_skip_sequence, record_length, record_type=b" "
):
    line_values = {}
    clear_line_values = line_values.clear

    seek = infile.seek
    read = infile.read

    row_length = record_length - 1
    while True:
        sep = read(1)
        if sep == record_type:
            clear_line_values()
            row = read(row_length)
            for name, start, end in field_skip_sequence:
                if name:
                    line_values[name] = row[start:end]
            yield line_values
        elif sep in (b"\x1a", b""):
            break
        else:
            seek(row_length, 1)


def read_rows_with_row_skipping(
    infile, row_skip_sequence, record_length, record_type=b" "
):
    line_values = {}
    clear_line_values = line_values.clear

    read = infile.read
    seek = infile.seek

    row_length = record_length - 1
    while True:
        sep = read(1)
        if sep == record_type:
            for read_row, length, field_seq in row_skip_sequence:
                if not read_row:
                    seek(length, 1)
                else:
                    clear_line_values()
                    # Note: lines_values is the only variable used
                    #       all yielded dicts are the same dict, but updated (caution)
                    row = read(row_length)
                    for name, start, end in field_seq:
                        if name:
                            line_values[name] = row[start:end]
                    yield line_values
        elif sep in (b"\x1a", b""):
            break
        else:
            seek(row_length, 1)


def read_float_file(
    infile, required_indices, record_length, fields, record_type=b" "
):
    tag_indices = []
    field_seq = float_field_parsing_sequence_counting(fields)
    for row in read_rows_without_row_skipping(
        infile, field_seq, record_length
    ):
        if row["Marker"] != b"B":
            infile.seek(-record_length, 1)
            break
        tag_index = int(row["TagIndex"])
        tag_indices.append(tag_index)
        if tag_index in required_indices:
            yield row
    required_parsed_indices = [i for i in required_indices if i in tag_indices]
    row_seq = float_row_parsing_sequence(
        record_length, required_parsed_indices, tag_indices, fields
    )
    later_rows = read_rows_with_row_skipping(
        infile, row_seq, record_length, record_type
    )

    tags_per_section = len(required_parsed_indices)
    first_row = {}
    while True:
        rows = islice(later_rows, tags_per_section)
        first_row = next(rows)
        yield first_row
        if first_row["Marker"] == b"E":
            yield from rows
            break
        yield from rows
    # except StopIteration:
    # yield from read_float_file(infile, required_indices, record_length, fields, record_type)

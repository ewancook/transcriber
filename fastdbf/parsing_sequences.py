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

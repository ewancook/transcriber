def create_row_skip_sequence(required_items, all_items, row_length):
    sequence = []
    for item in all_items:
        if item in required_items:
            sequence.extend([(True, row_length - 1), [False, 1]])
        elif len(sequence) and not sequence[-1][0]:
            sequence[-1][1] += row_length
        else:
            sequence.append([False, row_length])
    if not sequence[-1][0]:
        sequence[-1][1] -= 1
        if not sequence[-1][1]:
            sequence.pop()
    return sequence


def create_field_skip_sequence(required_fields, all_fields):
    sequence = []
    for item in all_fields:
        if item.name in required_fields:
            sequence.append((item.name, item.length))
        elif len(sequence) and not sequence[-1][0]:
            sequence[-1][1] += item.length
        else:
            sequence.append([False, item.length])
    return sequence

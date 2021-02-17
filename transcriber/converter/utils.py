from itertools import islice, takewhile

import fastdbf

TAG_INDEX = "TTagIndex"


def have_correct_tags(filenames, num_tags, encoding="cp437"):
    parser = Parser(required_fields=[TAG_INDEX])
    for filename in filenames:
        table = FastDBF(filename, [], encoding=encoding, recfactory=None)
        if (table.header.numrecords / num_tags).is_integer():
            parsed = islice(fastdbf.parse_float_fil(filename), 0, num_tags + 1)
            if len({s[TAG_INDEX] for s in parsed}) == num_tags:
                yield filename


def determine_total_tags(filenames, encoding="cp437"):
    for float_file, tag_file in filenames:
        yield (float_file, sum(1 for _ in fastdbf.parse_tag_file(tag_file)))

        # try:
        #     for row in takewhile(lambda r: r[TAG_INDEX] not in tags, table):
        #         tags.add(row[TAG_INDEX])
        #     yield (float_file, len(tags))
        # except KeyError:
        #     yield (float_file, 0)

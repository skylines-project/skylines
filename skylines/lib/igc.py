# -*- coding: utf-8 -*-

from skylines import files


def read_igc_header(igc_file):
    path = files.filename_to_path(igc_file.filename)

    try:
        f = file(path, 'r')
    except IOError:
        return

    i = 0
    for line in f:
        if line[0] == 'A' and len(line) >= 4:
            igc_file.logger_manufacturer_id = line[1:4]
        else:
            break

        # don't read more than 100 lines, that should be enough
        i += 1
        if i > 100:
            break

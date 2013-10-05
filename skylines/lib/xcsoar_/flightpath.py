import xcsoar
from skylines.lib import files


def flight_path(igc_file, max_points=1000):
    path = files.filename_to_path(igc_file.filename)
    return list(xcsoar.flight_path(path, max_points=max_points))

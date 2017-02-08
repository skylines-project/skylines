from datetime import date

from skylines.model import IGCFile


def simple(**kwargs):
    return IGCFile(
        filename='simple.igc',
        md5='ebc87aa50aec6a6667e1c9251a68a90e',
        date_utc=date(2011, 6, 18),
        **kwargs
    )

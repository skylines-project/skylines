from datetime import datetime

from skylines.model import Club


def lva(**kwargs):
    return Club(
        name=u"LV Aachen",
        website=u"http://www.lv-aachen.de",
        time_created=datetime(2015, 12, 24, 12, 34, 56),
    ).apply_kwargs(kwargs)


def sfn(**kwargs):
    return Club(
        name=u"Sportflug Niederberg", time_created=datetime(2017, 1, 1, 12, 34, 56)
    ).apply_kwargs(kwargs)

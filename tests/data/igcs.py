import os
from datetime import date, datetime

from skylines.model import IGCFile

simple_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simple.igc")
hornet_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "2018-04-14-fla-6ng-01.igc"
)
zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "igcs.zip")


def simple(owner, **kwargs):
    return IGCFile(
        owner=owner,
        filename="simple.igc",
        md5="ebc87aa50aec6a6667e1c9251a68a90e",
        date_utc=date(2011, 6, 18),
    ).apply_kwargs(kwargs)


def filled(owner, **kwargs):
    return IGCFile(
        owner=owner,
        time_created=datetime(2017, 1, 15, 21, 23, 40),
        filename="abc1234d.igc",
        md5="12345aa50aec6a6667e1c9251a68a90e",
        logger_id="GC1",
        logger_manufacturer_id="FLA",
        registration=u"D-4449",
        competition_id=u"TH",
        model=u"Hornet",
        date_utc=date(2017, 1, 15),
    ).apply_kwargs(kwargs)

# -*- coding: utf-8 -*-

import os
import datetime

from skylines.lib.igc import read_igc_headers


def test_empty_file():
    assert read_igc_headers([]) == {}


def test_simple_file():
    path = os.path.realpath(os.path.join(__file__, "..", "..", "data", "simple.igc"))

    assert read_igc_headers(path) == dict(
        manufacturer_id=u"XCS",
        logger_id=u"AAA",
        date_utc=datetime.date(2011, 6, 18),
        model=u"ASK13",
        reg=u"LY-KDR",
    )


def test_logger_information():
    assert read_igc_headers([b"AFLA6NG"]) == dict(
        manufacturer_id="FLA", logger_id="6NG"
    )


def test_filser_logger_id():
    assert read_igc_headers([b"AFIL01460FLIGHT:1"]) == dict(
        manufacturer_id="FIL", logger_id="14K"
    )


def test_date():
    headers = read_igc_headers([b"AFLA6NG", b"HFDTE150812"])

    assert "date_utc" in headers
    assert headers["date_utc"] == datetime.date(2012, 8, 15)


def test_date_only():
    assert read_igc_headers([b"HFDTE150812"]) == dict(
        date_utc=datetime.date(2012, 8, 15)
    )


def test_glider_information():
    headers = read_igc_headers(
        [
            b"AFLA6NG",
            b"HFDTE",
            b"HFGTYGLIDERTYPE:",
            b"HFGIDGLIDERID:",
            b"HFCIDCOMPETITIONID:",
        ]
    )

    assert "model" in headers
    assert headers["model"] == ""

    assert "reg" in headers
    assert headers["reg"] == ""

    assert "cid" in headers
    assert headers["cid"] == ""

    headers = read_igc_headers(
        [
            b"AFLA6NG",
            b"HFDTE150812",
            b"HFGTYGLIDERTYPE:HORNET",
            b"HFGIDGLIDERID:D_4449",
            b"HFCIDCOMPETITIONID:TH",
        ]
    )

    assert "model" in headers
    assert headers["model"] == "HORNET"

    assert "reg" in headers
    assert headers["reg"] == "D_4449"

    assert "cid" in headers
    assert headers["cid"] == "TH"

import pytest

from collections import namedtuple
from werkzeug.datastructures import Headers

T = namedtuple("TestData", ["available", "header", "result"])

TESTS = [
    T("de,en,fr", "fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5", "fr"),
    T("de,fr", "fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5", "fr"),
    T("de,en", "fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5", "en"),
    T("de,nl", "fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5", "de"),
    T("nl", "fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5", None),
]


@pytest.fixture(params=TESTS)
def testdata(request):
    return request.param


def test_locale_negotiation(client, testdata):
    headers = Headers()
    headers.add("Accept-Language", testdata.header)

    res = client.get("/locale?available=" + testdata.available, headers=headers)
    assert res.status_code == 200
    assert res.json == {u"locale": testdata.result}

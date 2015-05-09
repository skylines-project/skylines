import os
from io import BytesIO

import pytest

from skylines.database import db
from skylines.model import User

pytestmark = pytest.mark.usefixtures('db_session', 'files_folder')

HERE = os.path.dirname(__file__)
DATADIR = os.path.join(HERE, '..', '..', 'data')


@pytest.fixture(scope='function')
def bill(app):
    bill = User(first_name='bill',
                email_address='bill@example.com',
                password='pass')

    with app.app_context():
        db.session.add(bill)
        db.session.commit()

    return bill


@pytest.fixture(scope='function')
def logged_in_browser(browser, bill):
    form = browser.getForm(index=1)
    form.getControl(name='email_address').value = bill.email_address
    form.getControl(name='password').value = 'pass'
    form.submit()

    return browser


def test_upload_broken_igc(logged_in_browser):
    b = logged_in_browser
    b.open('/flights/upload')

    # we should be logged in now
    assert 'IGC or ZIP file(s)' in b.contents

    b.getControl('IGC or ZIP file(s)').add_file(BytesIO('broken'),
                                                'text/plain',
                                                '/tmp/broken.igc')
    b.getControl('Upload').click()
    assert 'No flight was saved.' in b.contents


def test_upload_single(logged_in_browser, bill):
    assert bill.id is not None
    b = logged_in_browser
    b.open('/flights/upload')

    # we should be logged in now
    assert 'IGC or ZIP file(s)' in b.contents

    f_igc = open(os.path.join(DATADIR, 'simple.igc'))
    b.getControl('IGC or ZIP file(s)').add_file(f_igc,
                                                'text/plain',
                                                '/tmp/simple.igc')

    b.getControl('Upload').click()

    assert 'Your flights have been saved.' in b.contents

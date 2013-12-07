import os
from io import BytesIO
from nose.tools import assert_is_not_none, assert_in

from tests.functional import TestController
from skylines.model import db, User

HERE = os.path.dirname(__file__)
DATADIR = os.path.join(HERE, '..', 'data')


class TestUpload(TestController):
    def setUp(self):
        super(TestUpload, self).setUp()

        self.bill = User(first_name='bill', email_address='bill@example.com',
                         password='pass')
        db.session.add(self.bill)
        db.session.commit()
        self.login('bill@example.com', 'pass')

    def login(self, email, password):
        form = self.browser.getForm(index=1)
        form.getControl(name='email_address').value = email
        form.getControl(name='password').value = password
        form.submit()

    def test_upload_broken_igc(self):
        b = self.browser
        b.open('/flights/upload')

        # we should be logged in now
        assert 'IGC or ZIP file(s)' in b.contents

        b.getControl('IGC or ZIP file(s)').add_file(BytesIO('broken'),
                                                    'text/plain',
                                                    '/tmp/broken.igc')
        b.getControl('Upload').click()
        assert 'No flight was saved.' in b.contents

    def test_upload_single(self):
        assert_is_not_none(self.bill.id)
        b = self.browser
        b.open('/flights/upload')

        # we should be logged in now
        assert_in('IGC or ZIP file(s)', b.contents)

        f_igc = open(os.path.join(DATADIR, 'simple.igc'))
        b.getControl('IGC or ZIP file(s)').add_file(f_igc,
                                                    'text/plain',
                                                    '/tmp/simple.igc')

        b.getControl('Upload').click()

        assert_in('Your flights have been saved.', b.contents)

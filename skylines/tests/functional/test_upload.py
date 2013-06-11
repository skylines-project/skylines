import os
from io import BytesIO
from nose.tools import (assert_is_not_none, assert_equal,
                        assert_true, assert_false)

from skylines.tests.functional import TestController
from skylines.model.auth import User
from skylines import db

HERE = os.path.dirname(__file__)


class TestUpload(TestController):
    def setUp(self):
        super(TestUpload, self).setUp()

        self.bill = User(name='bill', email_address='bill@example.com',
                         password='pass')
        db.session.add(self.bill)
        db.session.commit()
        self.login('bill@example.com', 'pass')

    def login(self, email, password):
        form = self.browser.getForm(index=1)
        form.getControl('Email Address:').value = 'bill@example.com'
        form.getControl('Password:').value = 'pass'
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
        assert 'IGC or ZIP file(s)' in b.contents

        f = open(os.path.join(HERE, 'data', 'simple.igc'))
        b.getControl('IGC or ZIP file(s)').add_file(f,
                                                    'text/plain',
                                                    '/tmp/simple.igc')
        b.getControl('Upload').click()
        assert 'Your flights have been saved.' in b.contents

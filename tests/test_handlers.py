from unittest import TestCase

from evalytics.handlers import SetupHandler, ReviewersHandler, SendMailHandler

from tests.common.mocks import RequestHandlerMock
from tests.common.mocks import MockMapper

class SetupHandlerSut(SetupHandler, RequestHandlerMock):
    'Inject mocks into SetupHandler dependencies'

class ReviewersHandlerSut(ReviewersHandler, RequestHandlerMock):
    'Inject mocks into ReviewersHandler dependencies'

class SendMailHandlerSut(SendMailHandler, RequestHandlerMock, MockMapper):
    'Inject mocks into SendMailHandler dependencies'

class TestSetupHandler(TestCase):

    def setUp(self):
        self.sut = SetupHandlerSut()

    def test_endpoint(self):
        self.assertEqual('/setup', self.sut.path)

class TestReviewersHandler(TestCase):

    def setUp(self):
        self.sut = ReviewersHandlerSut()

    def test_endpoint(self):
        self.assertEqual('/reviewers', self.sut.path)

class TestSendMailHandler(TestCase):

    def setUp(self):
        self.sut = SendMailHandlerSut()

    def test_endpoint(self):
        self.assertEqual('/evaldelivery', self.sut.path)

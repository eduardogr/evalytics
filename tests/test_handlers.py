from unittest import TestCase

from evalytics.handlers import SetupHandler, ReviewersHandler
from evalytics.handlers import EvalDeliveryHandler, ResponseStatusHandler
from evalytics.handlers import EvalReportsHandler, PeersAssignmentHandler

from tests.common.mocks import RequestHandlerMock
from tests.common.mocks import MockMapper

class SetupHandlerSut(SetupHandler, RequestHandlerMock):
    'Inject mocks into SetupHandler dependencies'

class ReviewersHandlerSut(ReviewersHandler, RequestHandlerMock):
    'Inject mocks into ReviewersHandler dependencies'

class EvalDeliveryHandlerSut(
        EvalDeliveryHandler, RequestHandlerMock, MockMapper):
    'Inject mocks into EvalDeliveryHandler dependencies'

class ResponseStatusHandlerSut(ResponseStatusHandler, RequestHandlerMock):
    'Inject mocks into ResponseStatusHandler dependencies'

class EvalReportsHandlerSut(EvalReportsHandler, RequestHandlerMock):
    'Inject mocks into EvalReportHandler dependencies'

class PeersAssignmentHandlerSut(PeersAssignmentHandler, RequestHandlerMock):
    'Inject mocks into PeersAssignmentHandler dependencies'

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

class TestEvalDeliveryHandler(TestCase):

    def setUp(self):
        self.sut = EvalDeliveryHandlerSut()

    def test_endpoint(self):
        self.assertEqual('/evaldelivery', self.sut.path)

class TestResponseStatusHandler(TestCase):

    def setUp(self):
        self.sut = ResponseStatusHandlerSut()

    def test_endpoint(self):
        self.assertEqual('/status', self.sut.path)

class TestEvalReportsHandler(TestCase):

    def setUp(self):
        self.sut = EvalReportsHandlerSut()

    def test_endpoint(self):
        self.assertEqual('/evalreports', self.sut.path)

class TestPeersAssignmentHandler(TestCase):

    def setUp(self):
        self.sut = PeersAssignmentHandlerSut()

    def test_endpoint(self):
        self.assertEqual('/peers', self.sut.path)

from unittest import TestCase

from evalytics.handlers import SetupHandler, ReviewersHandler, SendMailHandler
from evalytics.models import GoogleSetup, GoogleFile, Reviewer, Employee

from tests.common.mocks import RequestHandlerMock
from tests.common.mocks import SetupUseCaseMock, GetReviewersUseCaseMock
from tests.common.mocks import SendMailUseCaseMock
from tests.common.mocks import MockMapper
from tests.common.utils import async_test

class SetupHandlerSut(SetupHandler, RequestHandlerMock, SetupUseCaseMock):
    'Inject mocks into SetupHandler dependencies'

class ReviewersHandlerSut(ReviewersHandler, RequestHandlerMock, GetReviewersUseCaseMock):
    'Inject mocks into ReviewersHandler dependencies'

class SendMailHandlerSut(SendMailHandler, RequestHandlerMock, SendMailUseCaseMock, MockMapper):
    'Inject mocks into SendMailHandler dependencies'

class TestSetupHandler(TestCase):

    def setUp(self):
        self.sut = SetupHandlerSut()

    @async_test
    def test_post(self):
        google_setup = GoogleSetup(
            folder=GoogleFile(name='folder', id='unique'),
            files=[]
        )
        self.sut.set_setup(google_setup)

        yield from self.sut.post()

        finish_data = self.sut.get_finish_data()
        self.assertEqual(2, len(finish_data))
        self.assertIn('success', finish_data)
        self.assertTrue(finish_data['success'])

        self.assertIn('response', finish_data)
        self.assertIn('setup', finish_data['response'])

    def test_endpoint(self):
        self.assertEqual('/setup', self.sut.path)

class TestReviewersHandler(TestCase):

    def setUp(self):
        self.sut = ReviewersHandlerSut()

    @async_test
    def test_post(self):
        reviewers = {
            'uid1': Reviewer(
                employee=Employee('uid1@comp', manager='', area=''),
                evals=[]),
            'uid2': Reviewer(
                employee=Employee('uid2@comp', manager='', area=''),
                evals=[]),
            'uid3': Reviewer(
                employee=Employee('uid3@comp', manager='', area=''),
                evals=[]),
        }
        self.sut.set_get_reviewers(reviewers)

        yield from self.sut.get()

        finish_data = self.sut.get_finish_data()
        self.assertEqual(2, len(finish_data))
        self.assertIn('success', finish_data)
        self.assertTrue(finish_data['success'])

        self.assertIn('response', finish_data)
        self.assertIn('reviewers', finish_data['response'])
        self.assertEqual(3, len(finish_data['response']['reviewers']))

    def test_endpoint(self):
        self.assertEqual('/reviewers', self.sut.path)

class TestSendMailHandler(TestCase):

    def setUp(self):
        self.sut = SendMailHandlerSut()

    @async_test
    def test_sendmail(self):
        reviewers = {
            'uid1': Reviewer(
                employee=Employee('uid1@comp', manager='', area=''),
                evals=[]),
            'uid2': Reviewer(
                employee=Employee('uid2@comp', manager='', area=''),
                evals=[]),
            'uid3': Reviewer(
                employee=Employee('uid3@comp', manager='', area=''),
                evals=[]),
        }
        self.sut.set_argument('reviewers', reviewers)
        self.sut.set_reviewers(reviewers)
        self.sut.set_response(['uid1', 'uid2', 'uid3'], [])

        yield from self.sut.post()

        finish_data = self.sut.get_finish_data()
        self.assertEqual(2, len(finish_data))
        self.assertIn('success', finish_data)
        self.assertTrue(finish_data['success'])

        self.assertIn('response', finish_data)
        self.assertIn('evals_sent', finish_data['response'])
        self.assertIn('evals_not_sent', finish_data['response'])
        self.assertEqual(3, len(finish_data['response']['evals_sent']))
        self.assertEqual(0, len(finish_data['response']['evals_not_sent']))

    def test_endpoint(self):
        self.assertEqual('/sendmail', self.sut.path)

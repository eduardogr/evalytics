from unittest import TestCase

from evalytics.server.core import DataRepository, CommunicationsProvider
from evalytics.server.adapters import EmployeeAdapter
from evalytics.server.usecases import SetupUseCase
from evalytics.server.usecases import GetReviewersUseCase, SendMailUseCase
from evalytics.server.models import GoogleSetup, GoogleFile, Reviewer

from evalytics.tests.fixtures.employees import employees_collection

MOCK_FILENAME = 'mockfolder'
MOCK_FILEID = 'mockid'

class MockDataRepository(DataRepository):

    def setup_storage(self):
        folder = GoogleFile(name=MOCK_FILENAME, id=MOCK_FILEID)
        orgchart = GoogleFile(name=MOCK_FILENAME, id=MOCK_FILEID)
        return GoogleSetup(folder=folder, files=[orgchart])

    def get_employees(self):
        return {
            'em_email': employees_collection().get('em_email'),
            'manager_em': employees_collection().get('manager_em'),
        }

    def get_forms(self):
        return {}

class MockCommunicationsProvider(CommunicationsProvider):

    def __init__(self):
        self.raise_exception_for_reviewers = []

    def add_raise_exception_for_reviewer(self, reviewer_uid: str):
        self.raise_exception_for_reviewers.append(reviewer_uid)

    def send_communication(self, reviewer: Reviewer, data):
        if reviewer.uid in self.raise_exception_for_reviewers:
            raise Exception("MockCommunicationsProvider was asked to throw this exception")
        return

class MockEmployeeAdapter(EmployeeAdapter):

    def build_reviewers(self, employees, forms):
        return employees

    def build_eval_message(self, reviewer: Reviewer):
        return ""

class MockedSetupUseCase(SetupUseCase, MockDataRepository):
    'Inject a mock into the SetupUseCase dependency'

class MockedGetReviewersUseCase(
        GetReviewersUseCase,
        MockDataRepository,
        MockEmployeeAdapter):
    'Inject a mock into the GetReviewersUseCase dependency'

class MockedSendMailUseCase(
        SendMailUseCase,
        MockCommunicationsProvider,
        MockEmployeeAdapter):
    'Inject a mock into the SendEmailUseCase dependency'

class TestUseCases(TestCase):

    def test_setup_usecase(self):
        setup_usecase = MockedSetupUseCase()

        setup = setup_usecase.execute()

        self.assertEqual(MOCK_FILEID, setup.folder.id)
        self.assertEqual(MOCK_FILENAME, setup.folder.name)

    def test_get_reviewers_usecase(self):
        get_reviewers = MockedGetReviewersUseCase()

        reviewers = get_reviewers.execute()

        self.assertEqual(
            employees_collection().get('em_email'),
            reviewers['em_email'])

    def test_send_email_usecase(self):
        reviewers = {
            'em_email': employees_collection().get('em_email'),
            'manager_em': employees_collection().get('manager_em'),
        }
        send_mail = MockedSendMailUseCase()

        evals_sent, evals_not_sent = send_mail.send_mail(reviewers)

        self.assertIn('em_email', evals_sent)
        self.assertIn('manager_em', evals_sent)
        self.assertEqual(0, len(evals_not_sent))

    def test_send_email_usecase_when_exception(self):
        reviewers = {
            'em_email': employees_collection().get('em_email'),
            'manager_em': employees_collection().get('manager_em'),
        }
        send_mail = MockedSendMailUseCase()
        send_mail.add_raise_exception_for_reviewer(reviewers['manager_em'].uid)

        evals_sent, evals_not_sent = send_mail.send_mail(reviewers)

        self.assertIn('em_email', evals_sent)
        self.assertEqual(1, len(evals_sent))

        self.assertIn('manager_em', evals_not_sent)
        self.assertEqual(1, len(evals_not_sent))

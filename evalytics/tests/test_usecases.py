from unittest import TestCase

from evalytics.server.core import DataRepository, CommunicationsProvider
from evalytics.server.adapters import EmployeeAdapter
from evalytics.server.usecases import SetupUseCase, GetReviewersUseCase, SendMailUseCase
from evalytics.server.models import GoogleSetup, GoogleFile, Employee, Reviewer

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
            'best_employee': employees_collection().get('best_employee')
        }

    def get_forms(self):
        return {}

class MockCommunicationsProvider(CommunicationsProvider):

    def send_communication(self, employee: Employee, data):
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
            employees_collection().get('best_employee'),
            reviewers['best_employee'])

    def test_send_email_usecase(self):
        reviewers = {
            'best_employee': employees_collection().get('best_employee')
        }

        send_mail = MockedSendMailUseCase()
        send_mail.send_mail(reviewers)

        self.assertEqual(
            employees_collection().get('best_employee'),
            reviewers['best_employee'])

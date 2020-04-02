from unittest import TestCase

from evalytics.server.core import DataRepository, CommunicationsProvider
from evalytics.server.adapters import EmployeeAdapter
from evalytics.server.usecases import SetupUseCase, StartUseCase
from evalytics.server.models import GoogleSetup, GoogleFile, Employee

from evalytics.tests.fixtures.employees import employees

MOCK_FILENAME = 'mockfolder'
MOCK_FILEID = 'mockid'

class MockDataRepository(DataRepository):

    def setup_storage(self):
        folder = GoogleFile(name=MOCK_FILENAME, id=MOCK_FILEID)
        orgchart = GoogleFile(name=MOCK_FILENAME, id=MOCK_FILEID)
        return GoogleSetup(folder=folder, orgchart_file=orgchart)

    def get_employees(self):
        return [
            employees().get('best_employee')
        ]

class MockCommunicationsProvider(CommunicationsProvider):

    def send_communication(self, employee: Employee, data):
        return

class MockEmployeeAdapter(EmployeeAdapter):

    def build_eval_message(self, employee: Employee):
        return ""

class MockedSetupUseCase(SetupUseCase, MockDataRepository):
    'Inject a mock into the SetupUseCase dependency'

class MockedStartUseCase(
        StartUseCase, 
        MockDataRepository, 
        MockCommunicationsProvider,
        MockEmployeeAdapter):
    'Inject a mock into the StartUseCase dependency'

class TestUseCases(TestCase):

    def test_setup_usecase(self):
        setup_usecase = MockedSetupUseCase()

        setup = setup_usecase.execute()

        self.assertEqual(MOCK_FILEID, setup.folder.id)
        self.assertEqual(MOCK_FILENAME, setup.folder.name)

    def test_start_usecase(self):
        start_usecase = MockedStartUseCase()

        reviewers = start_usecase.execute()

        self.assertEqual(employees().get('best_employee'), reviewers[0])

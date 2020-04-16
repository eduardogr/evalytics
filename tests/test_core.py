from unittest import TestCase

from evalytics.storages import GoogleStorage
from evalytics.communications_channels import GmailChannel
from evalytics.core import DataRepository, CommunicationsProvider
from evalytics.models import Reviewer, Employee


class MockGoogleStorage(GoogleStorage):

    def setup(self):
        return

    def get_employee_map(self):
        return

    def get_forms_map(self):
        return

class MockedDataRepository(DataRepository, MockGoogleStorage):
    'Inject a mock into the DataRepository dependency'

class MockGmailChannel(GmailChannel):

    def send(self, reviewer: Reviewer, data):
        return

class MockedCommunicationsProvider(
        CommunicationsProvider,
        MockGmailChannel):
    'Inject a mock into the CommunicationsProvider dependency'

class TestCore(TestCase):

    def setUp(self):
        self.data_repository = MockedDataRepository()
        self.comms_provider = MockedCommunicationsProvider()

    def test_data_repository_setup_simple_call(self):
        self.data_repository.setup_storage()

    def test_data_repository_get_employees_simple_call(self):
        self.data_repository.get_employees()

    def test_data_repository_get_forms_simple_call(self):
        self.data_repository.get_forms()

    def test_communications_provider_send_communication_simple_call(self):
        employee = Employee(
            mail='myemail@email.com',
            manager='mymanager',
            area=None)
        reviewer = Reviewer(
            employee=employee,
            evals=[]
        )
        data = "this is ypur email"

        self.comms_provider.send_communication(reviewer, data)

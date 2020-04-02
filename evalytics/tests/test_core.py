from unittest import TestCase

from evalytics.server.storages import Storage
from evalytics.server.communications_channels import CommunicationChannel
from evalytics.server.core import DataRepository, CommunicationsProvider
from evalytics.server.models import Employee


class MockStorage(Storage):

    def setup(self):
        return

    def get_employee_list(self):
        return

class MockedDataRepository(DataRepository, MockStorage):
    'Inject a mock into the DataRepository dependency'

class MockCommunicationChannel(CommunicationChannel):

    def send(self, employee: Employee, data):
        return

class MockedCommunicationsProvider(
        CommunicationsProvider,
        MockCommunicationChannel):
    'Inject a mock into the CommunicationsProvider dependency'

class TestCore(TestCase):

    def setUp(self):
        self.data_repository = MockedDataRepository()
        self.comms_provider = MockedCommunicationsProvider()

    def test_data_repository_setup_simple_call(self):
        self.data_repository.setup_storage()

    def test_data_repository_get_employees_simple_call(self):
        self.data_repository.get_employees()

    def test_communications_provider_send_communication_simple_call(self):
        employee = Employee(
            mail='myemail@email.com',
            manager='mymanager',
            eval_180=None)
        data = "this is ypur email"

        self.comms_provider.send_communication(employee, data)

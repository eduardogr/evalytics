from unittest import TestCase

from evalytics.core import DataRepository, CommunicationsProvider
from evalytics.models import Reviewer, Employee

from tests.common.mocks import MockGoogleStorage, MockGmailChannel

class DataRepositorySut(DataRepository, MockGoogleStorage):
    'Inject a mock into the DataRepository dependency'

class CommunicationsProviderSut(
        CommunicationsProvider,
        MockGmailChannel):
    'Inject a mock into the CommunicationsProvider dependency'

class TestDataRepository(TestCase):

    def setUp(self):
        self.sut = DataRepositorySut()

    def test_setup_simple_call(self):
        self.sut.setup_storage()

    def test_get_employees_simple_call(self):
        self.sut.get_employees()

    def test_get_forms_simple_call(self):
        self.sut.get_forms()

class TestCommunicationsProvider(TestCase):

    def setUp(self):
        self.sut = CommunicationsProviderSut()

    def test_send_communication_simple_call(self):
        employee = Employee(
            mail='myemail@email.com',
            manager='mymanager',
            area=None)
        reviewer = Reviewer(
            employee=employee,
            evals=[]
        )
        data = "this is ypur email"

        self.sut.send_communication(reviewer, data)

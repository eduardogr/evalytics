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

    def test_setup_call(self):
        self.sut.setup_storage()

    def test_get_employees_call(self):
        self.sut.get_employees()

    def test_get_forms_call(self):
        self.sut.get_forms()

    def test_get_responses_call(self):
        self.sut.get_responses()

    def test_get_evaluations_call(self):
        self.sut.get_evaluations()

    def test_generate_eval_reports(self):
        self.sut.generate_eval_reports(
            dry_run=False,
            eval_process_id='',
            reviewee='martin',
            reviewee_evaluations=[],
            employee_managers=[]
        )

class TestCommunicationsProvider(TestCase):

    def setUp(self):
        self.sut = CommunicationsProviderSut()

    def test_send_communication_call(self):
        employee = Employee(
            mail='myemail@email.com',
            manager='mymanager',
            area=None)
        reviewer = Reviewer(
            employee=employee,
            evals=[]
        )
        mail_subject = 'any_subject'
        data = "this is your email"

        self.sut.send_communication(reviewer, mail_subject, data)

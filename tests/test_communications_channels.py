from unittest import TestCase

from evalytics.google_api import GoogleAPI
from evalytics.communications_channels import CommunicationChannelFactory, GmailChannel
from evalytics.models import Reviewer, Employee
from evalytics.config import ProvidersConfig

from tests.common.mocks import MockGoogleAPI, MockConfig

class CommunicationChannelFactorySut(CommunicationChannelFactory, MockConfig):
    'Inject a mock into CommunicationChannelFactory dependency'

class GmailChannelSut(GmailChannel, MockGoogleAPI):
    'Inject mocks into GmailChannel dependencies'

class TestCommunicationChannelFactory(TestCase):

    def setUp(self):
        self.sut = CommunicationChannelFactorySut()

    def test_get_google_storage(self):
        self.sut.set_communications_provider_provider(ProvidersConfig.GMAIL)

        comm_channel = self.sut.get_communication_channel()

        self.assertTrue(isinstance(comm_channel, GmailChannel))

    def test_get_not_existent_storage(self):
        self.sut.set_communications_provider_provider("NOT_EXISTENT")

        with self.assertRaises(ValueError):
            self.sut.get_communication_channel()

class TestGmailChannel(TestCase):

    def setUp(self):
        self.sut = GmailChannelSut()

        self.employee = Employee(
            mail='em@mail.com',
            manager='',
            area='some'
        )
        self.reviewer = Reviewer(
            employee=self.employee,
            evals=[]
        )
        self.any_mail_subject = 'any mail subject'

    def test_send_communication(self):
        expected_user_id = GoogleAPI.AUTHENTICATED_USER
        is_reminder = False

        self.sut.send_communication(
            reviewer=self.reviewer,
            is_reminder=is_reminder)

        calls = self.sut.get_send_message_calls()
        self.assertEqual(1, len(calls))
        self.assertEqual(expected_user_id, calls[0]['user_id'])
        self.assertIn('raw', calls[0]['message'])

    def test_send_communication_when_is_reminder(self):
        expected_user_id = GoogleAPI.AUTHENTICATED_USER
        is_reminder = True

        self.sut.send_communication(
            reviewer=self.reviewer,
            is_reminder=is_reminder)

        calls = self.sut.get_send_message_calls()
        self.assertEqual(1, len(calls))
        self.assertEqual(expected_user_id, calls[0]['user_id'])
        self.assertIn('raw', calls[0]['message'])

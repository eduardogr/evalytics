from unittest import TestCase

from evalytics.google_api import GoogleAPI
from evalytics.communications_channels import GmailChannel
from evalytics.models import Reviewer, Employee

from tests.common.mocks import MockGoogleAPI

class GmailChannelSut(GmailChannel, MockGoogleAPI):
    'Inject mocks into GmailChannel dependencies'

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

    def test_send_empty_message(self):
        expected_user_id = GoogleAPI.AUTHENTICATED_USER

        self.sut.send_communication(
            reviewer=self.reviewer,
            mail_subject=self.any_mail_subject,
            data='')

        calls = self.sut.get_send_message_calls()
        self.assertEqual(1, len(calls))
        self.assertEqual(expected_user_id, calls[0]['user_id'])
        self.assertIn('raw', calls[0]['message'])

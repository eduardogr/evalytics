from unittest import TestCase

from evalytics.google_api import GoogleAPI
from evalytics.communications_channels import CommunicationChannelFactory
from evalytics.communications_channels import GmailChannel, SlackChannel
from evalytics.models import Reviewer, Employee, Eval, EvalKind
from evalytics.config import ProvidersConfig

from tests.common.mocks import MockSlackClient, MockGoogleAPI, MockConfig

class CommunicationChannelFactorySut(CommunicationChannelFactory, MockConfig):
    'Inject a mock into CommunicationChannelFactory dependency'

class SlackChannelSut(SlackChannel, MockSlackClient, MockConfig):
    'Inject mocks into SlackChannel dependencies'

class GmailChannelSut(GmailChannel, MockGoogleAPI, MockConfig):
    'Inject mocks into GmailChannel dependencies'

class TestCommunicationChannelFactory(TestCase):

    def setUp(self):
        self.sut = CommunicationChannelFactorySut()

    def test_get_gmail_channel(self):
        self.sut.set_communications_provider_provider(ProvidersConfig.GMAIL)

        comm_channel = self.sut.get_communication_channel()

        self.assertTrue(isinstance(comm_channel, GmailChannel))

    def test_get_slack_channel(self):
        self.sut.set_communications_provider_provider(ProvidersConfig.SLACK)

        comm_channel = self.sut.get_communication_channel()

        self.assertTrue(isinstance(comm_channel, SlackChannel))

    def test_get_not_existent_storage(self):
        self.sut.set_communications_provider_provider("NOT_EXISTENT")

        with self.assertRaises(ValueError):
            self.sut.get_communication_channel()

class TestSlackChannel(TestCase):

    def setUp(self):
        self.sut = SlackChannelSut()
        self.sut.set_slack_message_is_direct(True)

        self.employee = Employee(
            mail='em@mail.com',
            manager='',
            area='some'
        )
        self.reviewer_with_no_evals = Reviewer(
            employee=self.employee,
            evals=[]
        )
        self.reviewer_with_self_eval = Reviewer(
            employee=self.employee,
            evals=[Eval(
                reviewee='uid',
                kind=EvalKind.SELF,
                form='any form')])
        self.reviewer_with_any_eval = Reviewer(
            employee=self.employee,
            evals=[Eval(
                reviewee='uid',
                kind=EvalKind.PEER_TO_PEER,
                form='any form')]
        )
        self.any_mail_subject = 'any mail subject'
        self.sut.set_slack_users_map({})

    def test_send_communication_when_reviewer_with_no_evals(self):
        reviewer = self.reviewer_with_no_evals
        is_reminder = False

        self.sut.send_communication(
            reviewer=reviewer,
            is_reminder=is_reminder)

        calls = self.sut.get_chat_post_message_calls()
        self.assertEqual(1, len(calls))
        self.assertIn(reviewer.uid, calls[0]['channel'])

    def test_send_communication_when_self_eval(self):
        reviewer = self.reviewer_with_self_eval
        is_reminder = True

        self.sut.send_communication(
            reviewer=reviewer,
            is_reminder=is_reminder)

        calls = self.sut.get_chat_post_message_calls()
        self.assertEqual(1, len(calls))
        self.assertIn(reviewer.uid, calls[0]['channel'])

    def test_send_communication_when_any_eval(self):
        reviewer = self.reviewer_with_any_eval
        is_reminder = True

        self.sut.send_communication(
            reviewer=reviewer,
            is_reminder=is_reminder)

        calls = self.sut.get_chat_post_message_calls()
        self.assertEqual(1, len(calls))
        self.assertIn(reviewer.uid, calls[0]['channel'])

    def test_send_communication_when_is_reminder(self):
        reviewer = self.reviewer_with_no_evals
        is_reminder = True

        self.sut.send_communication(
            reviewer=reviewer,
            is_reminder=is_reminder)

        calls = self.sut.get_chat_post_message_calls()
        self.assertEqual(1, len(calls))
        self.assertIn(reviewer.uid, calls[0]['channel'])

    def test_send_communication_when_is_direct_message(self):
        reviewer = self.reviewer_with_no_evals
        is_reminder = True
        self.sut.set_slack_message_is_direct(True)

        self.sut.send_communication(
            reviewer=reviewer,
            is_reminder=is_reminder)

        calls = self.sut.get_chat_post_message_calls()
        self.assertEqual(1, len(calls))
        self.assertIn(reviewer.uid, calls[0]['channel'])


    def test_send_communication_when_is_direct_message_and_reviewer_is_in_slack_user_map(self):
        reviewer = self.reviewer_with_no_evals
        is_reminder = True
        self.sut.set_slack_message_is_direct(True)
        self.sut.set_slack_users_map({
            reviewer.uid: 'mapped_user'
        })

        self.sut.send_communication(
            reviewer=reviewer,
            is_reminder=is_reminder)

        calls = self.sut.get_chat_post_message_calls()
        self.assertEqual(1, len(calls))
        self.assertIn('mapped_user', calls[0]['channel'])

    def test_send_communication_when_is_not_direct_message(self):
        reviewer = self.reviewer_with_no_evals
        is_reminder = True
        self.sut.set_slack_message_is_direct(False)

        self.sut.send_communication(
            reviewer=reviewer,
            is_reminder=is_reminder)

        calls = self.sut.get_chat_post_message_calls()
        self.assertEqual(1, len(calls))
        self.assertNotIn(reviewer.uid, calls[0]['channel'])

class TestGmailChannel(TestCase):

    def setUp(self):
        self.sut = GmailChannelSut()

        self.expected_user_id = GoogleAPI.AUTHENTICATED_USER
        self.employee = Employee(
            mail='em@mail.com',
            manager='',
            area='some'
        )
        self.reviewer_with_no_evals = Reviewer(
            employee=self.employee,
            evals=[]
        )
        self.reviewer_with_self_eval = Reviewer(
            employee=self.employee,
            evals=[Eval(
                reviewee='uid',
                kind=EvalKind.SELF,
                form='any form')])
        self.reviewer_with_any_eval = Reviewer(
            employee=self.employee,
            evals=[Eval(
                reviewee='uid',
                kind=EvalKind.PEER_TO_PEER,
                form='any form')]
        )
        self.any_mail_subject = 'any mail subject'

    def test_send_communication_when_reviewer_with_no_evals(self):
        is_reminder = False

        self.sut.send_communication(
            reviewer=self.reviewer_with_no_evals,
            is_reminder=is_reminder)

        calls = self.sut.get_send_message_calls()
        self.assertEqual(1, len(calls))
        self.assertEqual(self.expected_user_id, calls[0]['user_id'])
        self.assertIn('raw', calls[0]['message'])

    def test_send_communication_when_self_eval(self):
        is_reminder = True

        self.sut.send_communication(
            reviewer=self.reviewer_with_self_eval,
            is_reminder=is_reminder)

        calls = self.sut.get_send_message_calls()
        self.assertEqual(1, len(calls))
        self.assertEqual(self.expected_user_id, calls[0]['user_id'])
        self.assertIn('raw', calls[0]['message'])

    def test_send_communication_when_any_eval(self):
        is_reminder = True

        self.sut.send_communication(
            reviewer=self.reviewer_with_any_eval,
            is_reminder=is_reminder)

        calls = self.sut.get_send_message_calls()
        self.assertEqual(1, len(calls))
        self.assertEqual(self.expected_user_id, calls[0]['user_id'])
        self.assertIn('raw', calls[0]['message'])

    def test_send_communication_when_is_reminder(self):
        is_reminder = True

        self.sut.send_communication(
            reviewer=self.reviewer_with_no_evals,
            is_reminder=is_reminder)

        calls = self.sut.get_send_message_calls()
        self.assertEqual(1, len(calls))
        self.assertEqual(self.expected_user_id, calls[0]['user_id'])
        self.assertIn('raw', calls[0]['message'])

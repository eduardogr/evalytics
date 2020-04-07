from unittest import TestCase

from evalytics.client import CommandFactory
from evalytics.client import EvalyticsClient


class MockEvalyticsClient(EvalyticsClient):

    def __init__(self):
        self.calls = {}

    def print_reviewers(self):
        self.update_calls('print_reviewers')

    def send_eval(self):
        self.update_calls('send_eval')

    def retry_send_eval(self):
        self.update_calls('retry_send_eval')

    def help(self, command):
        self.update_calls('help')

    def update_calls(self, method):
        calls = 0
        if method in self.calls.keys():
            calls = self.calls[method]
        self.calls.update({
            method:(calls + 1)
        })

    def get_calls(self):
        return self.calls

class MockCommandFactory(CommandFactory, MockEvalyticsClient):
    'Inject a mock into the CommandFactory dependency'


class TestCommandFactory(TestCase):

    def test_command_factory_get_reviewers(self):
        factory = MockCommandFactory()
        factory.execute('get reviewers')

        self.assertIn('print_reviewers', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['print_reviewers'])

    def test_command_factory_send_eval(self):
        factory = MockCommandFactory()
        factory.execute('send evals')

        self.assertIn('send_eval', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['send_eval'])

    def test_command_factory_retry_send_eval(self):
        factory = MockCommandFactory()
        factory.execute('send evals --retry')

        self.assertIn('retry_send_eval', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['retry_send_eval'])

    def test_command_factory_help(self):
        factory = MockCommandFactory()
        factory.execute('invented command that is not expected')

        self.assertIn('help', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['help'])

from unittest import TestCase

from evalytics.server.mappers import Mapper
from evalytics.client import CommandFactory
from evalytics.client import EvalyticsClient
from evalytics.client import EvalyticsRequests


class MockMapper(Mapper):
    pass

class MockEvalyticsRequests(EvalyticsRequests):
    BASE_URL = "mock:8080"

    def setup(self):
        pass

    def reviewers(self):
        pass

    def sendmail(self, json_reviewers):
        pass

    def get_data_response(self, response):
        pass

class EvalyticsClientSut(EvalyticsClient, MockEvalyticsRequests, MockMapper):
    'Inject mocks into EvalyticsClient dependencies'

class MockEvalyticsClient(EvalyticsClient):

    def __init__(self):
        self.calls = {}

    def print_reviewers(self):
        self.update_calls('print_reviewers')

    def get_reviewers_stats(self):
        self.update_calls('get_reviewers_stats')

    def post_setup(self):
        self.update_calls('post_setup')

    def send_eval(self, whitelist=None):
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

class CommandFactorySut(CommandFactory, MockEvalyticsClient):
    'Inject a mock into the CommandFactory dependency'

class TestCommandFactory(TestCase):

    def test_command_factory_post_setup(self):
        factory = CommandFactorySut()
        factory.execute('post setup')

        self.assertIn('post_setup', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['post_setup'])

    def test_command_factory_get_reviewers(self):
        factory = CommandFactorySut()
        factory.execute('get reviewers')

        self.assertIn('print_reviewers', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['print_reviewers'])

    def test_command_factory_get_reviewers_stats(self):
        factory = CommandFactorySut()
        factory.execute('get reviewers --stats')

        self.assertIn('get_reviewers_stats', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['get_reviewers_stats'])

    def test_command_factory_send_eval(self):
        factory = CommandFactorySut()
        factory.execute('send evals')

        self.assertIn('send_eval', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['send_eval'])

    def test_command_factory_retry_send_eval(self):
        factory = CommandFactorySut()
        factory.execute('send evals --retry')

        self.assertIn('retry_send_eval', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['retry_send_eval'])

    def test_command_factory_help(self):
        factory = CommandFactorySut()
        factory.execute('invented command that is not expected')

        self.assertIn('help', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['help'])

class TestEvalyticsClient(TestCase):

    def test(self):
        pass

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
        self.show_stats = False
        self.dry_run = False

    def print_reviewers(self, show_stats=False):
        self.update_calls('print_reviewers')
        self.show_stats = show_stats

    def post_setup(self):
        self.update_calls('post_setup')

    def send_eval(self, whitelist=None, dry_run: bool = False):
        self.update_calls('send_eval')
        self.dry_run = dry_run

    def retry_send_eval(self, dry_run: bool = False):
        self.update_calls('retry_send_eval')
        self.dry_run = dry_run

    def whitelist_send_eval(self, dry_run: bool = False):
        self.update_calls('whitelist_send_eval')
        self.dry_run = dry_run

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

    def get_show_stats(self):
        return self.show_stats

    def get_dry_run(self):
        return self.dry_run

class CommandFactorySut(CommandFactory, MockEvalyticsClient):
    'Inject a mock into the CommandFactory dependency'

class TestCommandFactory(TestCase):

    def test_command_factory_post_setup(self):
        factory = CommandFactorySut()
        factory.execute('setup')

        self.assertIn('post_setup', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['post_setup'])

    def test_command_factory_get_reviewers(self):
        factory = CommandFactorySut()
        factory.execute('reviewers')

        self.assertIn('print_reviewers', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['print_reviewers'])

    def test_command_factory_get_reviewers_stats(self):
        factory = CommandFactorySut()
        factory.execute('reviewers --stats')

        self.assertIn('print_reviewers', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['print_reviewers'])
        self.assertTrue(factory.get_show_stats())

    def test_command_factory_send_eval(self):
        factory = CommandFactorySut()
        factory.execute('send_evals')

        self.assertIn('send_eval', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['send_eval'])

    def test_command_factory_send_eval_with_dry_run(self):
        factory = CommandFactorySut()
        factory.execute('send_evals --dry-run')

        self.assertIn('send_eval', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['send_eval'])
        self.assertTrue(factory.get_dry_run())

    def test_command_factory_retry_send_eval(self):
        factory = CommandFactorySut()
        factory.execute('send_evals --retry')

        self.assertIn('retry_send_eval', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['retry_send_eval'])

    def test_command_factory_retry_send_eval_with_dry_run(self):
        factory = CommandFactorySut()
        factory.execute('send_evals --retry --dry-run')

        self.assertIn('retry_send_eval', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['retry_send_eval'])
        self.assertTrue(factory.get_dry_run())

    def test_command_factory_whitelisted_send_eval(self):
        factory = CommandFactorySut()
        factory.execute('send_evals --whitelist')

        self.assertIn('whitelist_send_eval', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['whitelist_send_eval'])

    def test_command_factory_whitelisted_send_eval_with_dry_run(self):
        factory = CommandFactorySut()
        factory.execute('send_evals --whitelist --dry-run')

        self.assertIn('whitelist_send_eval', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['whitelist_send_eval'])
        self.assertTrue(factory.get_dry_run())

    def test_command_factory_help(self):
        factory = CommandFactorySut()
        factory.execute('invented command that is not expected')

        self.assertIn('help', factory.get_calls())
        self.assertEqual(1, factory.get_calls()['help'])

class TestEvalyticsClient(TestCase):

    def test(self):
        pass

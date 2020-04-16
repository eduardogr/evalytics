from unittest import TestCase

from client import CommandFactory
from client import EvalyticsClient
from client import EvalyticsRequests
from client import FileManager


class MockFile:
    def readlines(self):
        return []

    def close(self):
        return

class MockFileManager(FileManager):
    def open(self, filename: str, mode: str):
        return MockFile()

class MockEvalyticsRequests(EvalyticsRequests):
    BASE_URL = "mock:8080"

    def __init__(self):
        self.calls = {}
        self.setup_response = {}
        self.reviewers_response = {}
        self.sendmail_response = {}

    def set_setup_response(self, response):
        self.setup_response = response

    def setup(self):
        self.update_calls('setup')
        return True, self.setup_response

    def set_reviewers_response(self, response):
        self.reviewers_response = response

    def reviewers(self):
        self.update_calls('reviewers')
        return True, self.reviewers_response

    def set_sendmail_response(self, response):
        self.sendmail_response = response

    def sendmail(self, json_reviewers):
        self.update_calls('sendmail')
        return True, self.sendmail_response

    def get_data_response(self, response):
        self.update_calls('get_data_response')

    def update_calls(self, method):
        calls = 0
        if method in self.calls.keys():
            calls = self.calls[method]
        self.calls.update({
            method:(calls + 1)
        })

    def get_calls(self):
        return self.calls

class EvalyticsClientSut(EvalyticsClient, MockEvalyticsRequests, MockFileManager):
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

    def setUp(self):
        self.correct_reviewers_response = {
            'reviewers': [
                {
                    "employee": {
                        "uid": "uid1",
                        "mail": "uid1@company.com",
                        "manager": "",
                        "area": "Eng"
                    },
                    "evals": []
                },
                {
                    "employee": {
                        "uid": "uid2",
                        "mail": "uid2@company.com",
                        "manager": "",
                        "area": "Eng"
                    },
                    "evals": []
                },
                {
                    "employee": {
                        "uid": "uid3",
                        "mail": "uid3@company.com",
                        "manager": "",
                        "area": "Eng"
                    },
                    "evals": []
                },
            ]
        }

    def test_correct_setup(self):
        client = EvalyticsClientSut()
        client.set_setup_response({
            'setup': {
                'file': 'filename',
                'folder': 'foldername'
            }
        })

        client.post_setup()

        self.assertIn('setup', client.get_calls())
        self.assertEqual(1, client.get_calls()['setup'])

    def test_correct_reviewers(self):
        client = EvalyticsClientSut()
        client.set_reviewers_response({
            'reviewers': [
                'uid1',
                'uid2',
                'uid3'
            ]
        })

        client.get_reviewers()

        self.assertIn('reviewers', client.get_calls())
        self.assertEqual(1, client.get_calls()['reviewers'])

    def test_correct_print_reviewers(self):
        client = EvalyticsClientSut()
        client.set_reviewers_response({
            'reviewers': [
                {
                    "employee": {
                        "uid": "uid1"
                    },
                },
                {
                    "employee": {
                        "uid": "uid2"
                    },
                },
                {
                    "employee": {
                        "uid": "uid3"
                    },
                },
            ]
        })

        client.print_reviewers()

        self.assertIn('reviewers', client.get_calls())
        self.assertEqual(1, client.get_calls()['reviewers'])

    def test_correct_send_eval(self):
        client = EvalyticsClientSut()
        client.set_reviewers_response(self.correct_reviewers_response)
        client.set_sendmail_response({
            'evals_sent': ['uid1', 'uid2', 'uid3'],
            'evals_not_sent': []
        })
        whitelist = ['uid1', 'uid2', 'uid3']
        dry_run = False

        client.send_eval(whitelist=whitelist, dry_run=dry_run)

        self.assertIn('sendmail', client.get_calls())
        self.assertEqual(1, client.get_calls()['sendmail'])

    def test_correct_send_eval_with_whitelist(self):
        client = EvalyticsClientSut()
        client.set_reviewers_response(self.correct_reviewers_response)
        client.set_sendmail_response({
            'evals_sent': ['uid1', 'uid2', 'uid3'],
            'evals_not_sent': []
        })
        whitelist = ['uid1']
        dry_run = False

        client.send_eval(whitelist=whitelist, dry_run=dry_run)

        self.assertIn('sendmail', client.get_calls())
        self.assertEqual(1, client.get_calls()['sendmail'])

    def test_correct_send_eval_with_dry_run(self):
        client = EvalyticsClientSut()
        client.set_reviewers_response(self.correct_reviewers_response)
        client.set_sendmail_response({
            'evals_sent': ['uid1', 'uid2', 'uid3'],
            'evals_not_sent': []
        })
        whitelist = ['uid1', 'uid2', 'uid3']
        dry_run = True

        client.send_eval(whitelist=whitelist, dry_run=dry_run)

        self.assertNotIn('sendmail', client.get_calls())

    def test_correct_retry_send_eval_with_dry_run(self):
        client = EvalyticsClientSut()
        client.set_reviewers_response(self.correct_reviewers_response)
        client.set_sendmail_response({
            'evals_sent': ['uid1', 'uid2', 'uid3'],
            'evals_not_sent': []
        })
        dry_run = True

        client.retry_send_eval(dry_run=dry_run)

        self.assertNotIn('sendmail', client.get_calls())

    def test_correct_whitelist_send_eval_with_dry_run(self):
        client = EvalyticsClientSut()
        client.set_reviewers_response(self.correct_reviewers_response)
        client.set_sendmail_response({
            'evals_sent': ['uid1', 'uid2', 'uid3'],
            'evals_not_sent': []
        })
        dry_run = True

        client.whitelist_send_eval(dry_run=dry_run)

        self.assertNotIn('sendmail', client.get_calls())

    def test_correct_help(self):
        client = EvalyticsClientSut()

        client.help("some command")

        self.assertEqual(0, len(client.get_calls()))

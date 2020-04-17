from unittest import TestCase

from client import CommandFactory
from client import EvalyticsClient

from tests.common.mocks import MockFileManager
from tests.common.mocks import MockEvalyticsRequests, MockEvalyticsClient

class EvalyticsClientSut(
        EvalyticsClient,
        MockEvalyticsRequests,
        MockFileManager):
    'Inject mocks into EvalyticsClient dependencies'

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
        self.sut = EvalyticsClientSut()
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
        self.sut.set_setup_response({
            'setup': {
                'file': 'filename',
                'folder': 'foldername'
            }
        })

        self.sut.post_setup()

        self.assertIn('setup', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['setup'])

    def test_correct_reviewers(self):
        self.sut.set_reviewers_response({
            'reviewers': [
                'uid1',
                'uid2',
                'uid3'
            ]
        })

        self.sut.get_reviewers()

        self.assertIn('reviewers', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['reviewers'])

    def test_correct_print_reviewers(self):
        self.sut.set_reviewers_response({
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

        self.sut.print_reviewers()

        self.assertIn('reviewers', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['reviewers'])

    def test_correct_send_eval(self):
        self.sut.set_reviewers_response(self.correct_reviewers_response)
        self.sut.set_sendmail_response({
            'evals_sent': ['uid1', 'uid2', 'uid3'],
            'evals_not_sent': []
        })
        whitelist = ['uid1', 'uid2', 'uid3']
        dry_run = False

        self.sut.send_eval(whitelist=whitelist, dry_run=dry_run)

        self.assertIn('sendmail', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['sendmail'])

    def test_correct_send_eval_with_whitelist(self):
        self.sut.set_reviewers_response(self.correct_reviewers_response)
        self.sut.set_sendmail_response({
            'evals_sent': ['uid1', 'uid2', 'uid3'],
            'evals_not_sent': []
        })
        whitelist = ['uid1']
        dry_run = False

        self.sut.send_eval(whitelist=whitelist, dry_run=dry_run)

        self.assertIn('sendmail', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['sendmail'])

    def test_correct_send_eval_with_dry_run(self):
        self.sut.set_reviewers_response(self.correct_reviewers_response)
        self.sut.set_sendmail_response({
            'evals_sent': ['uid1', 'uid2', 'uid3'],
            'evals_not_sent': []
        })
        whitelist = ['uid1', 'uid2', 'uid3']
        dry_run = True

        self.sut.send_eval(whitelist=whitelist, dry_run=dry_run)

        self.assertNotIn('sendmail', self.sut.get_calls())

    def test_correct_retry_send_eval_with_dry_run(self):
        self.sut.set_reviewers_response(self.correct_reviewers_response)
        self.sut.set_sendmail_response({
            'evals_sent': ['uid1', 'uid2', 'uid3'],
            'evals_not_sent': []
        })
        dry_run = True

        self.sut.retry_send_eval(dry_run=dry_run)

        self.assertNotIn('sendmail', self.sut.get_calls())

    def test_correct_whitelist_send_eval_with_dry_run(self):
        self.sut.set_reviewers_response(self.correct_reviewers_response)
        self.sut.set_sendmail_response({
            'evals_sent': ['uid1', 'uid2', 'uid3'],
            'evals_not_sent': []
        })
        dry_run = True

        self.sut.whitelist_send_eval(dry_run=dry_run)

        self.assertNotIn('sendmail', self.sut.get_calls())

    def test_correct_help(self):
        self.sut.help("some command")

        self.assertEqual(0, len(self.sut.get_calls()))

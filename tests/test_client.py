from unittest import TestCase

from evalytics.models import Employee, Reviewer

from client import CommandFactory
from client import EvalyticsClient

from tests.common.mocks import MockFileManager, MockMapper
from tests.common.mocks import MockEvalyticsRequests, MockEvalyticsClient

class EvalyticsClientSut(
        EvalyticsClient,
        MockEvalyticsRequests,
        MockMapper,
        MockFileManager):
    'Inject mocks into EvalyticsClient dependencies'

class CommandFactorySut(CommandFactory, MockEvalyticsClient):
    'Inject a mock into the CommandFactory dependency'

class TestCommandFactory(TestCase):

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
        self.correct_status_response = {
            'status': {
                'completed': {},
                'inconsistent': {},
                'pending': [
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
        }
        self.sut = CommandFactorySut()
        self.sut.set_reviewers_response(self.correct_reviewers_response)
        self.sut.set_status_response(self.correct_status_response)

    def test_command_factory_post_setup(self):
        self.sut.execute(['setup'])

        self.assertIn('post_setup', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['post_setup'])

    def test_command_factory_get_reviewers(self):
        self.sut.execute(['reviewers'])

        self.assertIn('print_reviewers', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['print_reviewers'])

    def test_command_factory_get_reviewers_stats(self):
        self.sut.execute(['reviewers', '--stats'])

        self.assertIn('print_reviewers', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['print_reviewers'])
        self.assertTrue(self.sut.get_show_stats())

    def test_command_factory_send_eval(self):
        self.sut.execute(['send_evals'])

        self.assertIn('send_communication', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['send_communication'])

    def test_command_factory_send_eval_with_dry_run(self):
        self.sut.execute(['send_evals', '--dry-run'])

        self.assertIn('send_communication', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['send_communication'])
        self.assertTrue(self.sut.get_dry_run())

    def test_command_factory_retry_send_eval(self):
        self.sut.execute(['send_evals', '--retry'])

        self.assertIn('send_communication', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['send_communication'])

    def test_command_factory_retry_send_eval_with_dry_run(self):
        self.sut.execute(['send_evals', '--retry', '--dry-run'])

        self.assertIn('send_communication', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['send_communication'])
        self.assertTrue(self.sut.get_dry_run())

    def test_command_factory_whitelisted_send_communication(self):
        self.sut.execute(['send_evals', '--whitelist'])

        self.assertIn('send_communication', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['send_communication'])

    def test_command_factory_whitelisted_send_eval_with_dry_run(self):
        self.sut.execute(['send_evals', '--whitelist', '--dry-run'])

        self.assertIn('send_communication', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['send_communication'])
        self.assertTrue(self.sut.get_dry_run())

    def test_command_factory_send_reminder(self):
        self.sut.execute(['send_reminders'])

        self.assertIn('send_communication', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['send_communication'])

    def test_command_factory_send_reminder_with_dry_run(self):
        self.sut.execute(['send_reminders', '--dry-run'])

        self.assertIn('send_communication', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['send_communication'])
        self.assertTrue(self.sut.get_dry_run())

    def test_command_factory_retry_send_reminder(self):
        self.sut.execute(['send_reminders', '--retry'])

        self.assertIn('send_communication', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['send_communication'])

    def test_command_factory_retry_send_reminder_with_dry_run(self):
        self.sut.execute(['send_reminders', '--retry', '--dry-run'])

        self.assertIn('send_communication', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['send_communication'])
        self.assertTrue(self.sut.get_dry_run())

    def test_command_factory_whitelisted_send_reminder(self):
        self.sut.execute(['send_reminders', '--whitelist'])

        self.assertIn('send_communication', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['send_communication'])

    def test_command_factory_whitelisted_send_reminder_with_dry_run(self):
        self.sut.execute(['send_reminders', '--whitelist', '--dry-run'])

        self.assertIn('send_communication', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['send_communication'])
        self.assertTrue(self.sut.get_dry_run())

    def test_command_factory_help(self):
        self.sut.execute(['invented command that is not expected'])

        self.assertIn('help', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['help'])

    def test_command_factory_status(self):
        self.sut.execute(['status'])

        self.assertIn('print_status', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['print_status'])

    def test_command_factory_status_inconsistent_files(self):
        self.sut.execute(['status', '--inconsistent-files'])

        self.assertIn('print_inconsistent_files_status', self.sut.get_calls())
        self.assertEqual(
            1,
            self.sut.get_calls()['print_inconsistent_files_status'])

    def test_command_factory_reports(self):
        self.sut.execute(['reports'])

        self.assertIn('generate_reports', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['generate_reports'])

    def test_command_factory_reports_with_dry_run(self):
        self.sut.execute(['reports', '--dry-run'])

        self.assertIn('generate_reports', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['generate_reports'])
        self.assertTrue(self.sut.get_dry_run())

    def test_command_factory_whitelisted_reports(self):
        self.sut.execute(['reports', '--whitelist'])

        self.assertIn('generate_reports', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['generate_reports'])

    def test_command_factory_whitelisted_reports_with_dry_run(self):
        self.sut.execute(['reports', '--whitelist', '--dry-run'])

        self.assertIn('generate_reports', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['generate_reports'])
        self.assertTrue(self.sut.get_dry_run())

class TestEvalyticsClient(TestCase):

    def setUp(self):
        self.sut = EvalyticsClientSut()
        self.reviewers = {
            'uid1': Reviewer(
                employee=Employee(mail='uid1@', manager='',area='')
            ),
            'uid2': Reviewer(
                employee=Employee(mail='uid2@', manager='',area='')
            ),
            'uid3': Reviewer(
                employee=Employee(mail='uid3@', manager='',area='')
            ),
        }
        self.sut.set_reviewers(self.reviewers)
        self.sut.set_communications_response({
            'comms_sent': ['uid1', 'uid2', 'uid3'],
            'comms_not_sent': []
        })

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
        reviewers_response = {
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
        }
        self.sut.set_reviewers_response(reviewers_response)

        self.sut.print_reviewers()

        self.assertIn('reviewers', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['reviewers'])

    def test_correct_print_status(self):
        status_response = {
            'status': {
                "completed": {
                    "uid1": {
                        "reviewee": {
                            "kind": 'MANAGER_PEER',
                            "form": 'some form'
                        }
                    }
                },
                "pending": {
                    "uid2": {
                        "reviewee": {
                            "kind": 'MANAGER_PEER',
                            "form": 'some form'
                        }
                    }
                },
                "inconsistent": {
                    "uid3":  {
                        "reviewee": {
                            "kind": 'MANAGER_PEER',
                            "form": 'some form'
                        }
                    }
                },
            }
        }
        self.sut.set_status_response(status_response)

        self.sut.print_status()

        self.assertIn('status', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['status'])

    def test_correct_print_status_when_no_responses(self):
        status_response = {
            'status': {
                "completed": {},
                "pending": {},
                "inconsistent": {},
            }
        }
        self.sut.set_status_response(status_response)

        self.sut.print_status()

        self.assertIn('status', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['status'])

    def test_correct_print_inconsistent_files_status(self):
        status_response = {
            'status': {
                "completed": {},
                "pending": {},
                "inconsistent": {
                    "uid3":  {
                        "reviewee": {
                            "kind": 'MANAGER_PEER',
                            "form": 'some form',
                            "reason": "WRONG_REPORTER: tá tudo mal",
                            "filename": 'somefile',
                            "line_number": 2,
                        }
                    }
                },
            }
        }
        self.sut.set_status_response(status_response)

        self.sut.print_inconsistent_files_status()

        self.assertIn('status', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['status'])

    def test_correct_send_eval(self):
        kind = 'process_started'
        whitelist = ['uid1', 'uid2', 'uid3']
        dry_run = False

        self.sut.send_communication(kind=kind, reviewers=self.reviewers, whitelist=whitelist, dry_run=dry_run)

        self.assertIn('communications', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['communications'])

    def test_correct_send_eval_with_whitelist(self):
        kind = 'process_started'
        whitelist = ['uid1']
        dry_run = False

        self.sut.send_communication(kind=kind, reviewers=self.reviewers, whitelist=whitelist, dry_run=dry_run)

        self.assertIn('communications', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['communications'])

    def test_correct_send_eval_with_dry_run(self):
        kind = 'process_started'
        whitelist = ['uid1', 'uid2', 'uid3']
        dry_run = True

        self.sut.send_communication(kind=kind, reviewers=self.reviewers, whitelist=whitelist, dry_run=dry_run)

        self.assertNotIn('communications', self.sut.get_calls())

    def test_correct_send_reminders(self):
        kind = 'pending_evals_reminder'
        whitelist = ['uid1', 'uid2', 'uid3']
        dry_run = False

        self.sut.send_communication(kind=kind, reviewers=self.reviewers, whitelist=whitelist, dry_run=dry_run)

        self.assertIn('communications', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['communications'])

    def test_correct_send_reminder_with_whitelist(self):
        kind = 'pending_evals_reminder'
        whitelist = ['uid1']
        dry_run = False

        self.sut.send_communication(kind=kind, reviewers=self.reviewers, whitelist=whitelist, dry_run=dry_run)

        self.assertIn('communications', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['communications'])

    def test_correct_send_reminder_with_dry_run(self):
        kind = 'pending_evals_reminder'
        whitelist = ['uid1', 'uid2', 'uid3']
        dry_run = True

        self.sut.send_communication(kind=kind, reviewers=self.reviewers, whitelist=whitelist, dry_run=dry_run)

        self.assertNotIn('evaldelivery', self.sut.get_calls())

    def test_correct_whitelist_send_reminder_with_dry_run(self):
        kind = 'pending_evals_reminder'
        reviewers = []
        dry_run = True
        whitelist = ['uid1']

        self.sut.send_communication(kind=kind, reviewers=self.reviewers, whitelist=whitelist, dry_run=dry_run)

        self.assertNotIn('communications', self.sut.get_calls())

    def test_correct_generate_reports(self):
        self.sut.set_evalreports_response({
            'evals_reports': {
                'created': {
                    'uid1': {
                        'employee': 'uid1',
                        'managers': [
                            'uid2',
                            'uid3'
                        ]
                    },
                    'uid2': {
                        'employee': 'uid2',
                        'managers': [
                            'uid2', 
                            'uid3'
                        ]
                    },
                },
                'not_created': {}
            }
        })
        whitelist = ['uid1', 'uid2', 'uid3']
        dry_run = False

        self.sut.generate_reports(
            dry_run=dry_run,
            whitelist=whitelist)

        self.assertIn('evalreports', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['evalreports'])

    def test_correct_generate_reports_with_dry_run(self):
        self.sut.set_evalreports_response({
            'evals_reports': {
                'created': {
                    'uid1': {
                        'employee': 'uid1',
                        'managers': [
                            'uid2',
                            'uid3'
                        ]
                    },
                    'uid2': {
                        'employee': 'uid2',
                        'managers': [
                            'uid2', 
                            'uid3'
                        ]
                    },
                },
                'not_created': {}
            }
        })
        dry_run = True

        self.sut.generate_reports(dry_run=dry_run)

        self.assertIn('evalreports', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['evalreports'])

    def test_correct_whitelist_generate_reports_with_dry_run(self):
        self.sut.set_evalreports_response({
            'evals_reports': {
                'created': {
                    'uid1': {
                        'employee': 'uid1',
                        'managers': [
                            'uid2',
                            'uid3'
                        ]
                    },
                    'uid2': {
                        'employee': 'uid2',
                        'managers': [
                            'uid2', 
                            'uid3'
                        ]
                    },
                },
                'not_created': {}
            }
        })
        dry_run = True
        whitelist = ['uid1']

        self.sut.generate_reports(dry_run=dry_run, whitelist=whitelist)

        self.assertIn('evalreports', self.sut.get_calls())

    def test_correct_help(self):
        self.sut.help("some command")

        self.assertEqual(0, len(self.sut.get_calls()))

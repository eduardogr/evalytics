from unittest import TestCase

from evalytics.models import Employee, Reviewer

from client import CommandFactory
from client import EvalyticsClient

from tests.common.mocks import MockFileManager, MockMapper
from tests.common.mocks import MockEvalyticsRequests, MockEvalyticsClient
from tests.common.fixture import Fixture

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

    def test_command_factory_whitelisted_reports(self):
        self.sut.execute(['reports', '--whitelist'])

        self.assertIn('generate_reports', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['generate_reports'])

class TestEvalyticsClient(TestCase):

    def setUp(self):
        self.sut = EvalyticsClientSut()
        self.reviewers = Fixture().get_organization_reviewers()
        self.sut.set_reviewers(self.reviewers)
        self.sut.set_communications_response({
            'comms_sent': ['cto', 'tl1', 'tl2', 'sw1', 'sw2', 'sw3', 'sw4', 'sw5'],
            'comms_not_sent': []
        })

    def test_correct_reviewers(self):
        # given:
        self.sut.set_reviewers_response({
            'reviewers': [
                'cto',
                'tl1', 'tl2',
                'sw1', 'sw2', 'sw3', 'sw4', 'sw5'
            ]
        })

        # when:
        self.sut.get_reviewers()

        # then:
        self.assertIn('reviewers', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['reviewers'])

    def test_correct_print_reviewers(self):
        # given:
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

        # when:
        self.sut.print_reviewers()

        # then:
        self.assertIn('reviewers', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['reviewers'])

    def test_correct_print_status(self):
        # given:
        status_response = {
            'status': {
                "completed": {
                    "tl1": {
                        "reviewee": {
                            "kind": 'MANAGER_PEER',
                            "form": 'some form'
                        }
                    }
                },
                "pending": {
                    "tl2": {
                        "reviewee": {
                            "kind": 'MANAGER_PEER',
                            "form": 'some form'
                        }
                    }
                },
                "inconsistent": {
                    "sw1":  {
                        "reviewee": {
                            "kind": 'PEER_MANAGER',
                            "form": 'some form'
                        }
                    }
                },
            }
        }
        self.sut.set_status_response(status_response)

        # when:
        self.sut.print_status()

        # then:
        self.assertIn('status', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['status'])

    def test_correct_print_status_when_no_responses(self):
        # given:
        status_response = {
            'status': {
                "completed": {},
                "pending": {},
                "inconsistent": {},
            }
        }
        self.sut.set_status_response(status_response)

        # when:
        self.sut.print_status()

        # then:
        self.assertIn('status', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['status'])

    def test_correct_print_inconsistent_files_status(self):
        # given:
        status_response = {
            'status': {
                "completed": {},
                "pending": {},
                "inconsistent": {
                    "tl1":  {
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

        # when:
        self.sut.print_inconsistent_files_status()

        # then:
        self.assertIn('status', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['status'])

    def test_correct_send_eval(self):
        # given:
        kind = 'process_started'
        whitelist = ['cto', 'tl1', 'tl2']
        dry_run = False

        # when:
        self.sut.send_communication(kind=kind, reviewers=self.reviewers, whitelist=whitelist, dry_run=dry_run)

        # then:
        self.assertIn('communications', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['communications'])

    def test_correct_send_eval_with_whitelist(self):
        # given:
        kind = 'process_started'
        whitelist = ['tl1']
        dry_run = False

        # when:
        self.sut.send_communication(kind=kind, reviewers=self.reviewers, whitelist=whitelist, dry_run=dry_run)

        # then:
        self.assertIn('communications', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['communications'])

    def test_correct_send_eval_with_dry_run(self):
        # given:
        kind = 'process_started'
        whitelist = ['uid1', 'uid2', 'uid3']
        dry_run = True

        # when:
        self.sut.send_communication(kind=kind, reviewers=self.reviewers, whitelist=whitelist, dry_run=dry_run)

        # then:
        self.assertNotIn('communications', self.sut.get_calls())

    def test_correct_send_reminders(self):
        # given:
        kind = 'pending_evals_reminder'
        whitelist = ['tl1', 'tl2', 'sw1']
        dry_run = False

        # when:
        self.sut.send_communication(kind=kind, reviewers=self.reviewers, whitelist=whitelist, dry_run=dry_run)

        # then:
        self.assertIn('communications', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['communications'])

    def test_correct_send_reminder_with_whitelist(self):
        # given:
        kind = 'pending_evals_reminder'
        whitelist = ['tl1']
        dry_run = False

        # when:
        self.sut.send_communication(kind=kind, reviewers=self.reviewers, whitelist=whitelist, dry_run=dry_run)

        # then:
        self.assertIn('communications', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['communications'])

    def test_correct_send_reminder_with_dry_run(self):
        # given:
        kind = 'pending_evals_reminder'
        whitelist = ['cto', 'tl2', 'sw3']
        dry_run = True

        # when:
        self.sut.send_communication(kind=kind, reviewers=self.reviewers, whitelist=whitelist, dry_run=dry_run)

        # then:
        self.assertNotIn('evaldelivery', self.sut.get_calls())

    def test_correct_whitelist_send_reminder_with_dry_run(self):
        # given:
        kind = 'pending_evals_reminder'
        reviewers = {}
        dry_run = True
        whitelist = ['tl1']

        # when:
        self.sut.send_communication(kind=kind, reviewers=reviewers, whitelist=whitelist, dry_run=dry_run)

        # then:
        self.assertNotIn('communications', self.sut.get_calls())

    def test_correct_generate_reports(self):
        # given:
        self.sut.set_evalreports_response({
            'evals_reports': {
                'created': {
                    'tl1': {
                        'employee': 'tl1',
                        'managers': [
                            'cto',
                        ]
                    },
                    'sw1': {
                        'employee': 'sw1',
                        'managers': [
                            'tl1',
                            'cto'
                        ]
                    },
                },
                'not_created': {}
            }
        })
        whitelist = ['tl1', 'sw1']

        # when:
        self.sut.generate_reports(
            whitelist=whitelist)

        # then:
        self.assertIn('evalreports', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['evalreports'])

    def test_correct_generate_reports_with_dry_run(self):
        # given:
        self.sut.set_evalreports_response({
            'evals_reports': {
                'created': {
                    'tl1': {
                        'employee': 'tl1',
                        'managers': [
                            'cto',
                        ]
                    },
                    'tl2': {
                        'employee': 'tl2',
                        'managers': [
                            'cto',
                        ]
                    },
                },
                'not_created': {}
            }
        })

        # when:
        self.sut.generate_reports()

        # then:
        self.assertIn('evalreports', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['evalreports'])

    def test_correct_whitelist_generate_reports_with_dry_run(self):
        # given:
        self.sut.set_evalreports_response({
            'evals_reports': {
                'created': {
                    'tl1': {
                        'employee': 'tl1',
                        'managers': [
                            'cto',
                        ]
                    },
                    'sw2': {
                        'employee': 'sw2',
                        'managers': [
                            'tl1',
                            'cto'
                        ]
                    },
                },
                'not_created': {}
            }
        })
        whitelist = ['tl1']

        # when:
        self.sut.generate_reports(whitelist=whitelist)

        # then:
        self.assertIn('evalreports', self.sut.get_calls())
        self.assertEqual(1, self.sut.get_calls()['evalreports'])

    def test_correct_help(self):
        # when
        self.sut.help("some command")

        # then:
        self.assertEqual(0, len(self.sut.get_calls()))

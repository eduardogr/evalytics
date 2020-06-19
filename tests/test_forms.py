from unittest import TestCase

from evalytics.exceptions import MissingDataException
from evalytics.exceptions import MissingGoogleDriveFolderException
from evalytics.forms import ReviewerResponseKeyDictStrategy
from evalytics.models import ReviewerResponse
from evalytics.forms import FormsPlatformFactory, GoogleForms
from evalytics.config import ProvidersConfig

from tests.common.mocks import MockGoogleAPI, MockConfig

class FormsPlatformFactorySut(FormsPlatformFactory, MockConfig):
    'Inject a mock into FormsPlatformFactory dependency'

class GoogleFormsSut(GoogleForms, MockGoogleAPI, MockConfig):
    'Inject mocks into GoogleForms dependencies'

class TestFormsPlatformFactory(TestCase):

    def setUp(self):
        self.sut = FormsPlatformFactorySut()

    def test_get_google_forms_platform(self):
        self.sut.set_forms_platform_provider(ProvidersConfig.GOOGLE_FORMS)

        forms_platform = self.sut.get_forms_platform()

        self.assertTrue(isinstance(forms_platform, GoogleForms))

    def test_get_not_existent_forms_platform(self):
        self.sut.set_forms_platform_provider("NOT_EXISTENT")

        with self.assertRaises(ValueError):
            self.sut.get_forms_platform()

class TestGoogleForms(TestCase):

    def setUp(self):
        self.sut = GoogleFormsSut()

    def test_get_peers_assignment_ok_when_no_files(self):
        self.sut.set_folder_from_folder({'id': 'responses_folder'})
        self.sut.set_files_from_folder_response([])

        peers_assignment = self.sut.get_peers_assignment()

        self.assertEqual(0, len(peers_assignment))

    def test_get_peers_assignment_missing_folder_when_no_folder(self):
        with self.assertRaises(MissingGoogleDriveFolderException):
            self.sut.get_peers_assignment()

    def test_get_peers_assignment_ok_when_files(self):
        peer_assignment_file = [
            ['timestamp', 'who will review em1?', 'who will review em2?'],
            ['111111', 'em2,em3', 'em1,em3']
        ]
        self.sut.set_folder_from_folder({'id': 'responses_folder'})
        self.sut.set_files_from_folder_response([{
                'id': 'assignments from manager1',
                'name': 'Manager Evaluation By Team Member',
            }, {
                'id': 'assignments from manager2',
                'name': 'Report Evaluation by Manager',
            }, {
                'id': 'assignments from manager3',
                'name': 'Self Evaluation',
            },
        ])
        self.sut.set_file_rows_by_id('assignments from manager1', peer_assignment_file)
        self.sut.set_file_rows_by_id('assignments from manager2', peer_assignment_file)
        self.sut.set_file_rows_by_id('assignments from manager3', peer_assignment_file)

        peers_assignment = self.sut.get_peers_assignment()

        self.assertEqual(3, len(peers_assignment))
        self.assertIn('em1', peers_assignment)
        self.assertIn('em2', peers_assignment)
        self.assertIn('em3', peers_assignment)
        self.assertEqual(peers_assignment['em1'], ['em2'])
        self.assertEqual(peers_assignment['em2'], ['em1'])
        self.assertEqual(peers_assignment['em3'], ['em1', 'em2'])

    def test_get_responses_when_no_files(self):
        self.sut.set_folder_from_folder({'id': 'responses_folder'})
        self.sut.set_files_from_folder_response([])

        responses_map = self.sut.get_responses()

        self.assertEqual(0, len(responses_map))

    def test_get_responses_when_files(self):
        file_id_manager_by = 'file_id_manager_by'
        file_id_report_by = 'file_id_report_by'
        file_id_self = 'file_id_self'
        self.sut.set_folder_from_folder({'id': 'responses_folder'})
        self.sut.set_files_from_folder_response([{
                'id': file_id_manager_by,
                'name': 'Manager Evaluation By Team Member',
            }, {
                'id': file_id_report_by,
                'name': 'Report Evaluation by Manager',
            }, {
                'id': file_id_self,
                'name': 'Self Evaluation',
            },
        ])
        self.sut.set_file_rows_by_id(
            file_id_manager_by,
            [
                ['', 'reviewer', 'reviewee', 'question1', 'question2'],
                ['', 'reporter1', 'manager1', 'answer1', 'answer2']
            ]
        )
        self.sut.set_file_rows_by_id(
            file_id_report_by,
            [
                ['', 'reviewer', 'reviewee', 'question1', 'question2'],
                ['', 'manager1', 'reporter1', 'answer1', 'answer2']
            ]
        )
        self.sut.set_file_rows_by_id(
            file_id_self,
            [
                ['', 'reviewer', 'reviewee', 'question1', 'question2'],
                ['', 'reporter1', 'reporter1', 'answer1', 'answer2'],
                ['', 'reporter3', 'reporter3', 'answer1', 'answer2']
            ]
        )

        responses_map = self.sut.get_responses()

        self.assertEqual(3, len(responses_map))

        self.assertIn('reporter1', responses_map)
        self.assertIn('reporter3', responses_map)
        self.assertIn('manager1', responses_map)

        self.assertEqual(2, len(responses_map['reporter1']))
        self.assertEqual(1, len(responses_map['manager1']))
        self.assertEqual(1, len(responses_map['reporter3']))


    def test_get_responses_when_no_data_in_files(self):
        file_id_manager_by = 'file_id_manager_by'
        file_id_report_by = 'file_id_report_by'
        file_id_self = 'file_id_self'
        self.sut.set_folder_from_folder({'id': 'responses_folder'})
        self.sut.set_files_from_folder_response([{
                'id': file_id_manager_by,
                'name': 'Manager Evaluation By Team Member',
            }, {
                'id': file_id_report_by,
                'name': 'Report Evaluation by Manager',
            }, {
                'id': file_id_self,
                'name': 'Self Evaluation',
            },
        ])
        self.sut.set_file_rows_by_id(
            file_id_manager_by,
            []
        )
        self.sut.set_file_rows_by_id(
            file_id_report_by,
            []
        )
        self.sut.set_file_rows_by_id(
            file_id_self,
            []
        )

        with self.assertRaises(MissingDataException):
            self.sut.get_responses()

    def test_get_responses_when_uncompleted_data_in_files(self):
        file_id_manager_by = 'file_id_manager_by'
        file_id_report_by = 'file_id_report_by'
        file_id_self = 'file_id_self'
        self.sut.set_folder_from_folder({'id': 'responses_folder'})
        self.sut.set_files_from_folder_response([{
                'id': file_id_manager_by,
                'name': 'Manager Evaluation By Team Member',
            }, {
                'id': file_id_report_by,
                'name': 'Report Evaluation by Manager',
            }, {
                'id': file_id_self,
                'name': 'Self Evaluation',
            },
        ])
        self.sut.set_file_rows_by_id(
            file_id_manager_by,
            [
                ['', 'reviewer', 'reviewee', 'question1', 'question2'],
                ['', 'reporternswer1', 'answer2']
            ]
        )
        self.sut.set_file_rows_by_id(
            file_id_report_by,
            [
                ['', 'reviewer', 'reviewee', 'question1', 'question2'],
                ['', 'managernswer1', 'answer2']
            ]
        )
        self.sut.set_file_rows_by_id(
            file_id_self,
            [
                ['', 'reviewer', 'reviewee', 'question1', 'question2'],
                ['', 'reporteswer1', 'answer2'],
                ['', 'reporter3', 'reporter3', 'answer1', 'answer2']
            ]
        )

        with self.assertRaises(MissingDataException):
            self.sut.get_responses()

    def test_get_evaluations_correct_when_no_files(self):
        # given:
        self.sut.set_folder_from_folder({'id': 'responses_folder'})
        self.sut.set_files_from_folder_response([])

        # when:
        evaluations = self.sut.get_evaluations()

        # then:
        self.assertEqual(0, len(evaluations))

class TestReviewerResponseKeyDictStrategy(TestCase):

    def setUp(self):
        self.reviewer_response = ReviewerResponse(
            reviewer='reviewer',
            reviewee='reviewee',
            eval_kind='kind',
            eval_response='eval',
            filename='name',
            line_number=0
        )

        self.sut = ReviewerResponseKeyDictStrategy()

    def test_get_key_for_reviewee(self):
        # given:
        strategy = ReviewerResponseKeyDictStrategy.REVIEWEE_EVALUATION

        # when:
        key = self.sut.get_key(strategy, self.reviewer_response)

        # then:
        self.assertEqual('reviewee', key)

    def test_get_key_for_reviewer(self):
        # given:
        strategy = ReviewerResponseKeyDictStrategy.REVIEWER_RESPONSE

        # when:
        key = self.sut.get_key(strategy, self.reviewer_response)

        # then:
        self.assertEqual('reviewer', key)

    def test_get_key_for_non_implemented_strategy(self):
        with self.assertRaises(NotImplementedError):
            self.sut.get_key(
                'THIS_STRATEGY_DOES_NOT_EXIST',
                self.reviewer_response)

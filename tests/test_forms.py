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

        self.file_id_manager_by = 'file_id_manager_by'
        self.file_id_report_by = 'file_id_report_by'
        self.file_id_self = 'file_id_self'
        self.file_id_peer = 'file_id_peer'

        self.assignments_manager_1 = 'assignments for manager1'
        self.assignments_manager_2 = 'assignments for manager2'
        self.assignments_manager_3 = 'assignments for manager3'

    def test_get_peers_assignment_ok_when_no_files(self):
        self.sut.set_folder_from_folder({'id': 'responses_folder'})
        self.sut.set_files_from_folder_response([])

        peers_assignment = self.sut.get_peers_assignment()['peers']

        self.assertEqual(0, len(peers_assignment))

    def test_get_peers_assignment_missing_folder_when_no_folder(self):
        with self.assertRaises(MissingGoogleDriveFolderException):
            self.sut.get_peers_assignment()['peers']

    def test_get_peers_assignment_ok_when_files(self):
        self.__given_files_within_assignments_folder()
        peer_assignment_file = [
            [
                'who will review em1?',
                'who will review em2?',
                'who will review em3?',
                'who will review em4?',
                'who will review em5?',
            ],
            [
                'sre1, em4',
                'em3',
                'pmo1, em2',
                'em1, sre1',
                'pmo1, se1'
            ]
        ]
        self.sut.set_file_rows_by_id(self.assignments_manager_1, peer_assignment_file)
        self.sut.set_file_rows_by_id(self.assignments_manager_2, peer_assignment_file)
        self.sut.set_file_rows_by_id(self.assignments_manager_3, peer_assignment_file)

        peers_assignment = self.sut.get_peers_assignment()['peers']

        self.assertEqual(7, len(peers_assignment))
        self.assertIn('em1', peers_assignment)
        self.assertIn('em2', peers_assignment)
        self.assertIn('em3', peers_assignment)
        self.assertIn('em4', peers_assignment)
        self.assertIn('sre1', peers_assignment)
        self.assertIn('se1', peers_assignment)
        self.assertIn('pmo1', peers_assignment)
        self.assertEqual(1, len(peers_assignment['em1']))
        self.assertEqual(1, len(peers_assignment['em2']))
        self.assertEqual(1, len(peers_assignment['em3']))
        self.assertEqual(1, len(peers_assignment['em4']))
        self.assertEqual(2, len(peers_assignment['sre1']))
        self.assertEqual(1, len(peers_assignment['se1']))
        self.assertEqual(2, len(peers_assignment['pmo1']))
        self.assertEqual(peers_assignment['em1'], ['em4'])
        self.assertEqual(peers_assignment['em2'], ['em3'])
        self.assertEqual(peers_assignment['em3'], ['em2'])
        self.assertEqual(peers_assignment['em4'], ['em1'])
        self.assertEqual(peers_assignment['sre1'], ['em1', 'em4'])
        self.assertEqual(peers_assignment['se1'], ['em5'])
        self.assertEqual(peers_assignment['pmo1'], ['em3', 'em5'])

    def test_get_peers_assignment_ok_when_repeated_reviewees(self):
        self.__given_files_within_assignments_folder()
        peer_assignment_file = [
            ['who will review em1?', 'who will review em2?'],
            ['em3,em3,em3', 'em3,em3']
        ]
        self.sut.set_file_rows_by_id(self.assignments_manager_1, peer_assignment_file)
        self.sut.set_file_rows_by_id(self.assignments_manager_2, peer_assignment_file)
        self.sut.set_file_rows_by_id(self.assignments_manager_3, peer_assignment_file)

        peers_assignment = self.sut.get_peers_assignment()['peers']

        self.assertEqual(1, len(peers_assignment))
        self.assertIn('em3', peers_assignment)
        self.assertEqual(2, len(peers_assignment['em3']))
        self.assertEqual(peers_assignment['em3'], ['em1', 'em2'])

    def test_get_responses_when_no_files(self):
        self.sut.set_folder_from_folder({'id': 'responses_folder'})
        self.sut.set_files_from_folder_response([])

        responses_map = self.sut.get_responses()

        self.assertEqual(0, len(responses_map))

    def test_get_responses_when_files(self):
        self.__given_files_within_response_folder()
        self.__set_file_responses(self.file_id_manager_by, [['', 'reporter1', 'manager1', 'answer1', 'answer2']])
        self.__set_file_responses(self.file_id_report_by, [['', 'manager1', 'reporter1', 'answer1', 'answer2']])
        self.__set_file_responses(self.file_id_self, [
            ['', 'reporter1', 'reporter1', 'answer1', 'answer2'],
            ['', 'reporter3', 'reporter3', 'answer1', 'answer2']
        ])
        self.__set_file_responses(self.file_id_peer, [
            ['', 'reporter1', 'reporter2', 'answer1', 'answer2'],
            ['', 'reporter3', 'reporter2', 'answer1', 'answer2']
        ])

        responses_map = self.sut.get_responses()

        self.assertEqual(3, len(responses_map))

        self.assertIn('reporter1', responses_map)
        self.assertIn('reporter3', responses_map)
        self.assertIn('manager1', responses_map)

        self.assertEqual(3, len(responses_map['reporter1']))
        self.assertEqual(1, len(responses_map['manager1']))
        self.assertEqual(2, len(responses_map['reporter3']))

    def test_get_responses_when_no_data_in_files(self):
        self.__given_files_within_response_folder()
        self.sut.set_file_rows_by_id(self.file_id_manager_by, [])
        self.sut.set_file_rows_by_id(self.file_id_report_by, [])
        self.sut.set_file_rows_by_id(self.file_id_self, [])
        self.sut.set_file_rows_by_id(self.file_id_peer, [])

        with self.assertRaises(MissingDataException):
            self.sut.get_responses()

    def test_get_responses_when_uncompleted_data_in_files(self):
        self.__given_files_within_response_folder()
        self.__set_file_responses(self.file_id_manager_by, [['', 'reporternswer1', 'answer2']])
        self.__set_file_responses(self.file_id_report_by, [['', 'reporternswer1', 'answer2']])
        self.__set_file_responses(self.file_id_self, [
            ['', 'reporteswer1', 'answer2'],
            ['', 'reporter3', 'reporter3', 'answer1', 'answer2']
        ])

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

    def __given_files_within_assignments_folder(self):
        self.sut.set_folder_from_folder({'id': 'assignments_folder'})
        self.sut.set_files_from_folder_response([{
            'id': self.assignments_manager_1,
            'name': self.assignments_manager_1,
        }, {
            'id': self.assignments_manager_2,
            'name': self.assignments_manager_2,
        }, {
            'id': self.assignments_manager_3,
            'name': self.assignments_manager_3,
        }])

    def __given_files_within_response_folder(self):
        self.sut.set_folder_from_folder({'id': 'responses_folder'})
        self.sut.set_files_from_folder_response([{
            'id': self.file_id_manager_by,
            'name': 'Manager Evaluation By Team Member',
        }, {
            'id': self.file_id_report_by,
            'name': 'Report Evaluation by Manager',
        }, {
            'id': self.file_id_self,
            'name': 'Self Evaluation',
        }, {
            'id': self.file_id_peer,
            'name': 'Peer Evaluation',
        }, {
            'id': 'NO_ID',
            'name': 'None evalkind file',
        }])

    def __set_file_responses(self, file_id, responses):
        file_response = []
        file_response.append(['', 'reviewer', 'reviewee', 'question1', 'question2'])
        for response in responses:
            file_response.append(response)

        self.sut.set_file_rows_by_id(file_id, file_response)

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

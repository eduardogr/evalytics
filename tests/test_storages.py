from unittest import TestCase

from evalytics.storages import GoogleStorage
from evalytics.exceptions import MissingDataException, NoFormsException
from evalytics.models import EvalKind

from tests.common.mocks import MockGoogleAPI, MockConfig

class GoogleStorageSut(GoogleStorage, MockGoogleAPI, MockConfig):
    'Inject mocks into GoogleStorage dependencies'

class TestGoogleStorage(TestCase):

    def setUp(self):
        self.sut = GoogleStorageSut()

    def test_setup_when_setup_files_not_exist(self):
        self.sut.set_needed_spreadhseets([
            "google_orgchart",
            "google_formap"
        ])

        setup = self.sut.setup()

        self.assertEqual(2, len(setup.files))

    def test_setup_when_no_files_needed(self):
        self.sut.set_needed_spreadhseets([])

        setup = self.sut.setup()

        self.assertEqual(0, len(setup.files))
        self.assertEqual('folder_id', setup.folder.id)

    def test_setup_when_folder_exists_with_no_files(self):
        self.sut.set_folder({
            'parents': ['folders_parent'],
            'id': 'folder_id'
        })
        self.sut.set_needed_spreadhseets([
            "google_orgchart",
            "google_formap"
        ])

        setup = self.sut.setup()

        self.assertEqual(2, len(setup.files))

    def test_setup_when_setup_files_exist(self):
        self.sut.set_folder({
            'parents': ['folders_parent'],
            'id': 'folder_id'
        })
        self.sut.set_needed_spreadhseets([
            "google_orgchart",
            "google_formap"
        ])
        self.sut.set_fileid_by_name(
            folder_id='folder_id',
            filename="google_orgchart",
            fileid="google_orgchart")
        self.sut.set_fileid_by_name(
            folder_id='folder_id',
            filename="google_form_map",
            fileid="google_form_map")

        setup = self.sut.setup()

        self.assertEqual(2, len(setup.files))

    def test_setup_when_just_one_setup_file_exists(self):
        self.sut.set_folder({
            'parents': ['folders_parent'],
            'id': 'folder_id'
        })
        self.sut.set_needed_spreadhseets([
            "google_orgchart",
            "google_formap"
        ])
        self.sut.set_fileid_by_name(
            folder_id='folder_id',
            filename="google_form_map",
            fileid="google_form_map")

        setup = self.sut.setup()

        self.assertEqual(2, len(setup.files))

    def test_get_employee_map_correct_when_no_values(self):
        employees = self.sut.get_employee_map()

        self.assertEqual(0, len(employees))

    def test_get_employee_map_correct_when_non_repeated_mails(self):
        self.sut.set_file_rows_response([
            ['employee_juan@mail', 'manager', 'area'],
            ['employee_fulanito@mail', 'manager', 'area'],
        ])

        employees = self.sut.get_employee_map()

        self.assertEqual(2, len(employees))

    def test_get_employee_map_correct_when_repeated_mails(self):
        self.sut.set_file_rows_response([
            ['employee_juan@mail', 'manager', 'area'],
            ['employee_juan@mail', 'last-manager', 'area'],
        ])

        employees = self.sut.get_employee_map()

        self.assertEqual(1, len(employees))
        self.assertEqual('last-manager', employees['employee_juan'].manager)

    def test_get_employee_map_when_missing_data(self):
        self.sut.set_file_rows_response([
            ['employee@mail', 'manager', 'area'],
            ['employee@mail', 'manager'],
        ])

        with self.assertRaises(MissingDataException):
            self.sut.get_employee_map()

    def test_get_forms_map_correct_when_no_values_raise_excpetion(self):
        with self.assertRaises(NoFormsException):
            self.sut.get_forms_map()

    def test_get_forms_map_correct_when_non_repeated_areas(self):
        self.sut.set_file_rows_response([
            ['area1', 'form-self', 'form-manager', 'form-peer'],
            ['area2', 'form-self', 'form-manager', 'form-peer'],
        ])

        forms = self.sut.get_forms_map()

        self.assertEqual(2, len(forms))

    def test_get_forms_map_correct_when_repeated_areas(self):
        self.sut.set_file_rows_response([
            ['area1', 'form-self', 'form-manager', 'form-peer'],
            ['area1', 'last-form-self', 'last-form-manager', 'last-form-peer'],
        ])

        forms = self.sut.get_forms_map()

        self.assertEqual(1, len(forms))
        self.assertEqual('last-form-self', forms['area1'][EvalKind.SELF])

    def test_get_forms_map_when_missing_data(self):
        self.sut.set_file_rows_response([
            ['area1', 'form-self', 'form-manager', 'form-peer'],
            ['area2', 'form-self', 'form-manager'],
        ])

        with self.assertRaises(MissingDataException):
            self.sut.get_forms_map()

    def test_get_responses_map_when_no_files(self):
        self.sut.set_folder_from_folder({'id': 'responses_folder'})
        self.sut.set_files_from_folder_response([])

        responses_map = self.sut.get_responses_map()

        self.assertEqual(0, len(responses_map))

    def test_get_responses_map_when_files(self):
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

        responses_map = self.sut.get_responses_map()

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
            self.sut.get_responses_map()

    def test_get_responses_map_when_uncompleted_data_in_files(self):
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
            self.sut.get_responses_map()
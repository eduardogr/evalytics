from unittest import TestCase

from evalytics.storages import GoogleStorage
from evalytics.storages import StorageFactory
from evalytics.exceptions import MissingDataException, NoFormsException
from evalytics.models import EvalKind, ReviewerResponse
from evalytics.config import Config

from tests.common.mocks import MockGoogleAPI, MockConfig

class StorageFactorySut(StorageFactory, MockConfig):
    'Inject a mock into StorageFactory dependency'

class GoogleStorageSut(GoogleStorage, MockGoogleAPI, MockConfig):
    'Inject mocks into GoogleStorage dependencies'

class TestStorageFactory(TestCase):

    def setUp(self):
        self.sut = StorageFactorySut()

    def test_get_google_storage(self):
        self.sut.set_storage_provider(Config.STORAGE_PROVIDER_GOOGLE)

        storage = self.sut.get_storage()

        self.assertTrue(isinstance(storage, GoogleStorage))

    def test_get_not_existent_storage(self):
        self.sut.set_storage_provider("NOT_EXISTENT")

        with self.assertRaises(ValueError):
            self.sut.get_storage()

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

    def test_get_employees_correct_when_no_values(self):
        employees = self.sut.get_employees()

        self.assertEqual(0, len(employees))

    def test_get_employees_correct_when_non_repeated_mails(self):
        self.sut.set_file_rows_response([
            ['employee_juan@mail', 'manager', 'area'],
            ['employee_fulanito@mail', 'manager', 'area'],
        ])

        employees = self.sut.get_employees()

        self.assertEqual(2, len(employees))

    def test_get_employees_correct_when_repeated_mails(self):
        self.sut.set_file_rows_response([
            ['employee_juan@mail', 'manager', 'area'],
            ['employee_juan@mail', 'last-manager', 'area'],
        ])

        employees = self.sut.get_employees()

        self.assertEqual(1, len(employees))
        self.assertEqual('last-manager', employees['employee_juan'].manager)

    def test_get_employees_when_missing_data(self):
        self.sut.set_file_rows_response([
            ['employee@mail', 'manager', 'area'],
            ['employee@mail', 'manager'],
        ])

        with self.assertRaises(MissingDataException):
            self.sut.get_employees()

    def test_get_forms_correct_when_no_values_raise_excpetion(self):
        with self.assertRaises(NoFormsException):
            self.sut.get_forms()

    def test_get_forms_correct_when_non_repeated_areas(self):
        self.sut.set_file_rows_response([
            ['area1', 'form-self', 'form-manager', 'form-peer'],
            ['area2', 'form-self', 'form-manager', 'form-peer'],
        ])

        forms = self.sut.get_forms()

        self.assertEqual(2, len(forms))

    def test_get_forms_correct_when_repeated_areas(self):
        self.sut.set_file_rows_response([
            ['area1', 'form-self', 'form-manager', 'form-peer'],
            ['area1', 'last-form-self', 'last-form-manager', 'last-form-peer'],
        ])

        forms = self.sut.get_forms()

        self.assertEqual(1, len(forms))
        self.assertEqual('last-form-self', forms['area1'][EvalKind.SELF])

    def test_get_forms_when_missing_data(self):
        self.sut.set_file_rows_response([
            ['area1', 'form-self', 'form-manager', 'form-peer'],
            ['area2', 'form-self', 'form-manager'],
        ])

        with self.assertRaises(MissingDataException):
            self.sut.get_forms()

    def test_generate_eval_reports_when_files(self):
        # given:
        dry_run = False
        eval_process_id = 'anyprocessid'
        reviewee = 'pepe'
        reviewee_evaluations = [
            ReviewerResponse(
                reviewee=reviewee,
                reviewer=reviewee,
                eval_kind=EvalKind.SELF,
                eval_response=(),
                filename="filename",
                line_number=10
            )
        ]
        employee_managers = ['jefe', 'manager']

        # when:
        employee_managers_response = self.sut.generate_eval_reports(
            dry_run,
            eval_process_id,
            reviewee,
            reviewee_evaluations,
            employee_managers)

        # then:
        self.assertEqual(2, len(employee_managers_response))

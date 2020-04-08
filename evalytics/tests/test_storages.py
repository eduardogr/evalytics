from unittest import TestCase

from evalytics.server.storages import Storage, GoogleStorage
from evalytics.server.google_api import GoogleAPI
from evalytics.server.config import Config
from evalytics.server.exceptions import MissingDataException, NoFormsException
from evalytics.server.models import EvalKind

class MockStorage(Storage):

    def get_employee_map(self):
        return {}
    
    def get_forms_map(self):
        return {}

    def setup(self):
        pass

class MockGoogleAPI(GoogleAPI):

    def __init__(self):
        self.response = []
        self.folder = None
        self.fileid_by_name = {}

    def get_file_rows(self, foldername: str, filename: str, rows_range: str):
        return self.response

    def get_folder(self, name: str):
        return self.folder

    def create_folder(self, name: str):
        folder = {
            'parents': ['folders_parent'],
            'id': 'folder_id'
        }
        self.set_folder(folder)
        return self.folder

    def get_file_id_from_folder(self, folder_id: str, filename: str):
        if folder_id in self.fileid_by_name:
            if filename in self.fileid_by_name[folder_id]:
                return self.fileid_by_name[folder_id][filename]
        return None

    def create_spreadhsheet(self, folder_parent: str, folder, filename: str):
        spreasheet_id = filename
        self.set_fileid_by_name(folder['id'], spreasheet_id, spreasheet_id)
        return spreasheet_id

    def set_file_rows_response(self, response):
        self.response = response

    def set_folder(self, folder):
        self.folder = folder

    def set_fileid_by_name(self, folder_id: str, filename: str, fileid: str):
        self.fileid_by_name.update({
            folder_id: {
                filename: fileid
            }
        })

class MockConfig(Config):

    def __init__(self):
        super().__init__()
        self.needed_spreadsheets = []

    def read_google_folder(self):
        return "google_folder"

    def read_google_orgchart(self):
        return "google_orgchart"

    def read_google_form_map(self):
        return "google_form_map"

    def read_needed_spreadsheets(self):
        return self.needed_spreadsheets

    def set_needed_spreadhseets(self, needed_spreadhseets):
        self.needed_spreadsheets = needed_spreadhseets

class MockGoogleStorage(GoogleStorage, MockStorage, MockGoogleAPI, MockConfig):
    'Inject mocks into GoogleStorage dependencies'


class TestGoogleStorage(TestCase):

    def test_storage_setup_when_setup_files_not_exist(self):
        mock_google_storage = MockGoogleStorage()
        mock_google_storage.set_needed_spreadhseets([
            "google_orgchart",
            "google_formap"
        ])

        setup = mock_google_storage.setup()

        self.assertEqual(2, len(setup.files))

    def test_storage_setup_when_no_files_needed(self):
        mock_google_storage = MockGoogleStorage()
        mock_google_storage.set_needed_spreadhseets([])

        setup = mock_google_storage.setup()

        self.assertEqual(0, len(setup.files))
        self.assertEqual('folder_id', setup.folder.id)

    def test_storage_setup_when_folder_exists_with_no_files(self):
        mock_google_storage = MockGoogleStorage()
        mock_google_storage.set_folder({
            'parents': ['folders_parent'],
            'id': 'folder_id'
        })
        mock_google_storage.set_needed_spreadhseets([
            "google_orgchart",
            "google_formap"
        ])

        setup = mock_google_storage.setup()

        self.assertEqual(2, len(setup.files))

    def test_storage_setup_when_setup_files_exist(self):
        mock_google_storage = MockGoogleStorage()
        mock_google_storage.set_folder({
            'parents': ['folders_parent'],
            'id': 'folder_id'
        })
        mock_google_storage.set_needed_spreadhseets([
            "google_orgchart",
            "google_formap"
        ])
        mock_google_storage.set_fileid_by_name(
            folder_id='folder_id',
            filename="google_orgchart",
            fileid="google_orgchart")
        mock_google_storage.set_fileid_by_name(
            folder_id='folder_id',
            filename="google_form_map",
            fileid="google_form_map")

        setup = mock_google_storage.setup()

        self.assertEqual(2, len(setup.files))

    def test_storage_setup_when_just_one_setup_file_exists(self):
        mock_google_storage = MockGoogleStorage()
        mock_google_storage.set_folder({
            'parents': ['folders_parent'],
            'id': 'folder_id'
        })
        mock_google_storage.set_needed_spreadhseets([
            "google_orgchart",
            "google_formap"
        ])
        mock_google_storage.set_fileid_by_name(
            folder_id='folder_id',
            filename="google_form_map",
            fileid="google_form_map")

        setup = mock_google_storage.setup()

        self.assertEqual(2, len(setup.files))

    def test_storage_get_employee_map_correct_when_no_values(self):
        mock_google_storage = MockGoogleStorage()

        employees = mock_google_storage.get_employee_map()

        self.assertEqual(0, len(employees))

    def test_storage_get_employee_map_correct_when_non_repeated_mails(self):
        mock_google_storage = MockGoogleStorage()
        mock_google_storage.set_file_rows_response([
            ['employee_juan@mail', 'manager', 'area'],
            ['employee_fulanito@mail', 'manager', 'area'],
        ])

        employees = mock_google_storage.get_employee_map()

        self.assertEqual(2, len(employees))

    def test_storage_get_employee_map_correct_when_repeated_mails(self):
        mock_google_storage = MockGoogleStorage()
        mock_google_storage.set_file_rows_response([
            ['employee_juan@mail', 'manager', 'area'],
            ['employee_juan@mail', 'last-manager', 'area'],
        ])

        employees = mock_google_storage.get_employee_map()

        self.assertEqual(1, len(employees))
        self.assertEqual('last-manager', employees['employee_juan'].manager)

    def test_storage_get_employee_map_when_missing_data(self):
        mock_google_storage = MockGoogleStorage()
        mock_google_storage.set_file_rows_response([
            ['employee@mail', 'manager', 'area'],
            ['employee@mail', 'manager'],
        ])

        with self.assertRaises(MissingDataException):
            mock_google_storage.get_employee_map()

    def test_storage_get_forms_map_correct_when_no_values_raise_excpetion(self):
        mock_google_storage = MockGoogleStorage()

        with self.assertRaises(NoFormsException):
            mock_google_storage.get_forms_map()

    def test_storage_get_forms_map_correct_when_non_repeated_areas(self):
        mock_google_storage = MockGoogleStorage()
        mock_google_storage.set_file_rows_response([
            ['area1', 'form-self', 'form-manager', 'form-peer'],
            ['area2', 'form-self', 'form-manager', 'form-peer'],
        ])

        forms = mock_google_storage.get_forms_map()

        self.assertEqual(2, len(forms))

    def test_storage_get_forms_map_correct_when_repeated_areas(self):
        mock_google_storage = MockGoogleStorage()
        mock_google_storage.set_file_rows_response([
            ['area1', 'form-self', 'form-manager', 'form-peer'],
            ['area1', 'last-form-self', 'last-form-manager', 'last-form-peer'],
        ])

        forms = mock_google_storage.get_forms_map()

        self.assertEqual(1, len(forms))
        self.assertEqual('last-form-self', forms['area1'][EvalKind.SELF])

    def test_storage_get_forms_map_when_missing_data(self):
        mock_google_storage = MockGoogleStorage()
        mock_google_storage.set_file_rows_response([
            ['area1', 'form-self', 'form-manager', 'form-peer'],
            ['area2', 'form-self', 'form-manager'],
        ])

        with self.assertRaises(MissingDataException):
            mock_google_storage.get_forms_map()


class TestStorage(TestCase):

    def test_storage_setup_will_raise_exception(self):
        with self.assertRaises(NotImplementedError):
            Storage().setup()

    def test_storage_get_employee_map_will_raise_exception(self):
        with self.assertRaises(NotImplementedError):
            Storage().get_employee_map()

    def test_storage_get_forms_map_will_raise_exception(self):
        with self.assertRaises(NotImplementedError):
            Storage().get_forms_map()

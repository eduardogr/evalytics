from unittest import TestCase

from googledrive.exceptions import MissingGoogleDriveFolderException
from googledrive.exceptions import MissingGoogleDriveFileException

from evalytics.storages import GoogleStorage
from evalytics.storages import StorageFactory
from evalytics.exceptions import MissingDataException, NoFormsException
from evalytics.models import GoogleFile, EvalKind, ReviewerResponse
from evalytics.config import ProvidersConfig

from tests.common.mocks import MockGoogleAPI, MockConfig

class StorageFactorySut(StorageFactory, MockConfig):
    'Inject a mock into StorageFactory dependency'

class GoogleStorageSut(GoogleStorage, MockGoogleAPI, MockConfig):
    'Inject mocks into GoogleStorage dependencies'

class TestStorageFactory(TestCase):

    def setUp(self):
        self.sut = StorageFactorySut()

    def test_get_google_storage(self):
        self.sut.set_storage_provider(ProvidersConfig.GOOGLE_DRIVE)

        storage = self.sut.get_storage()

        self.assertTrue(isinstance(storage, GoogleStorage))

    def test_get_not_existent_storage(self):
        self.sut.set_storage_provider("NOT_EXISTENT")

        with self.assertRaises(ValueError):
            self.sut.get_storage()

class TestGoogleStorage(TestCase):

    def setUp(self):
        self.sut = GoogleStorageSut()

    def tearDown(self):
        self.sut.clear_gdrive_list_fixture()
        self.sut.clear_gdrive_get_file_fixture()

    def test_get_employees_correct_when_no_values(self):
        employees = self.sut.get_employees()

        self.assertEqual(0, len(employees))

    def test_get_employees_when_number_of_employees_is_zero(self):
        # given:
        self.sut.set_company_number_of_employees(0)

        # when:
        employees = self.sut.get_employees()

        # then:
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
            ['area1', 'form-self', 'form-manager', 'form-report', 'peer-peer'],
            ['area2', 'form-self', 'form-manager', 'form-report', 'peer-peer'],
        ])

        forms = self.sut.get_forms()

        self.assertEqual(2, len(forms))

    def test_get_forms_correct_when_repeated_areas(self):
        self.sut.set_file_rows_response([
            ['area1', 'form-self', 'form-manager', 'form-report', 'peer-peer'],
            ['area1', 'last-form-self', 'last-form-manager', 'last-form-report', 'last-peer-peer'],
        ])

        forms = self.sut.get_forms()

        self.assertEqual(1, len(forms))
        self.assertEqual('last-form-self', forms['area1'][EvalKind.SELF.name])

    def test_get_forms_when_missing_data(self):
        self.sut.set_file_rows_response([
            ['area1', 'form-self', 'form-manager', 'form-peer', 'peer-peer'],
            ['area2', 'form-self', 'form-manager'],
        ])

        with self.assertRaises(MissingDataException):
            self.sut.get_forms()

    def test_generate_eval_reports_when_files(self):
        # given:
        foldername = 'google_folder'
        eval_reports_folder = 'eval_reports_folder'
        eval_report_filename = 'PREFIX: pepe'
        eval_report_file_id = 'guarevar'

        eval_reports_file = GoogleFile(
            id=eval_report_file_id,
            name=eval_report_filename,
            parents=[eval_reports_folder])

        self.sut.set_gdrive_get_file_response(
            f"/{foldername}/{eval_reports_folder}/{eval_report_filename}",
            eval_reports_file)

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
            reviewee,
            reviewee_evaluations,
            employee_managers)

        # then:
        self.assertEqual(2, len(employee_managers_response))

    def test_generate_eval_reports_when_no_reports_folder(self):
        # given:
        foldername = 'google_folder'
        eval_reports_folder_name = 'eval_reports_folder'
        eval_report_filename = 'PREFIX: pepe' # TODO: get prefix from mock object
        self.sut.set_gdrive_get_file_raise_exception(f'/{foldername}/{eval_reports_folder_name}/{eval_report_filename}')

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
        with self.assertRaises(MissingGoogleDriveFolderException):
            self.sut.generate_eval_reports(
                reviewee,
                reviewee_evaluations,
                employee_managers)

    def test_generate_eval_reports_when_no_eval_report_does_not_exist(self):
        # given:
        foldername = 'google_folder'
        eval_reports_folder_name = 'eval_reports_folder'
        eval_reports_folder_id = 'guarevar'

        eval_reports_folder = GoogleFile(
            id=eval_reports_folder_id,
            name=eval_reports_folder_name,
            parents=[foldername])

        self.sut.set_gdrive_get_file_response(
            f"/{foldername}/{eval_reports_folder}",
            eval_reports_folder)

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
                reviewee,
                reviewee_evaluations,
                employee_managers)

        # then:
        self.assertEqual(2, len(employee_managers_response))

    def test_generate_eval_reports_when_files_and_add_comenter_is_enabled(self):
        # given:
        foldername = 'google_folder'
        eval_reports_folder = 'eval_reports_folder'
        eval_report_filename = 'PREFIX: pepe' # TODO: get prefix from mock object
        eval_report_file_id = 'guarevar'

        eval_report_file = GoogleFile(
            id=eval_report_file_id,
            name=eval_report_filename,
            parents=[eval_reports_folder])

        self.sut.set_gdrive_get_file_response(
            f"/{foldername}/{eval_reports_folder}/{eval_report_filename}",
            eval_report_file)

        self.sut.set_get_file_values_response(
            eval_report_file_id, [
                ['reviewer1', 'peer1,peer2'],
                ['reviewer2', 'peer1,peer2']])

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
        employee_managers = ['jefe', 'manager']

        self.sut.set_is_add_comenter_to_evals_reports_enabled(True)

        # when:
        employee_managers_response = self.sut.generate_eval_reports(
            reviewee,
            reviewee_evaluations,
            employee_managers)

        # then:
        self.assertEqual(2, len(employee_managers_response))

    def test_get_peers_assignment(self):
        # given:
        foldername = 'google_folder'
        assignments_folder = 'assignments_folder'
        peer_assignmetns_filename = 'assignments_peers_file'
        peer_file_id = 'guarevar'
        peer_assignments_file = GoogleFile(
            id=peer_file_id,
            name=peer_assignmetns_filename,
            parents=[assignments_folder])

        self.sut.set_gdrive_get_file_response(
            f"/{foldername}/{assignments_folder}/{peer_assignmetns_filename}",
            peer_assignments_file)

        self.sut.set_get_file_values_response(
            peer_file_id, [
                ['reviewer1', 'peer1,peer2'],
                ['reviewer2', 'peer1,peer2']])

        # when:
        peers = self.sut.get_peers_assignment()

        # then:
        self.assertEqual(2, len(peers))

    def test_get_peers_assignment_when_no_peers(self):
        # given:
        foldername = 'google_folder'
        assignments_folder = 'assignments_folder'
        peer_assignmetns_filename = 'assignments_peers_file'
        peer_file_id = 'guarevar'
        peer_assignments_file = GoogleFile(
            id=peer_file_id,
            name=peer_assignmetns_filename,
            parents=[assignments_folder])

        self.sut.set_gdrive_get_file_response(
            f"/{foldername}/{assignments_folder}/{peer_assignmetns_filename}",
            peer_assignments_file)

        self.sut.set_get_file_values_response(
            peer_file_id,
            [])

        # when:
        peers = self.sut.get_peers_assignment()

         # then:
        self.assertEqual(0, len(peers))

    def test_get_peers_assignment_when_missing_data_exception(self):
        # given:
        foldername = 'google_folder'
        assignments_folder = 'assignments_folder'
        peer_assignmetns_filename = 'assignments_peers_file'
        peer_file_id = 'guarevar'
        peer_assignments_file = GoogleFile(
            id=peer_file_id,
            name=peer_assignmetns_filename,
            parents=[assignments_folder])

        self.sut.set_gdrive_get_file_response(
            f"/{foldername}/{assignments_folder}/{peer_assignmetns_filename}",
            peer_assignments_file)

        self.sut.set_get_file_values_response(
            peer_file_id, [
            ['reviewer1', 'peer1,peer2'],
            ['reviewer2']
        ])

        # when:
        with self.assertRaises(MissingDataException):
            self.sut.get_peers_assignment()

    def test_write_peers_assignment_when_no_peers(self):
        # given:
        foldername = 'google_folder'
        assignments_folder = 'assignments_folder'
        peer_assignmetns_filename = 'assignments_peers_file'
        peer_file_id = 'guarevar'
        peer_assignments_file = GoogleFile(
            id=peer_file_id,
            name=peer_assignmetns_filename,
            parents=[assignments_folder])

        self.sut.set_gdrive_get_file_response(
            f"/{foldername}/{assignments_folder}/{peer_assignmetns_filename}",
            peer_assignments_file)

        self.sut.set_get_file_values_response(
            peer_file_id, [
            ['reviewer1', 'peer1,peer2'],
            ['reviewer2']
        ])
        no_peers = {}

        # when:
        self.sut.write_peers_assignment(no_peers)

    def test_write_peers_assignment_when_peers(self):
        # given:
        foldername = 'google_folder'
        assignments_folder = 'assignments_folder'
        peer_assignmetns_filename = 'assignments_peers_file'
        peer_file_id = 'guarevar'
        peer_assignments_file = GoogleFile(
            id=peer_file_id,
            name=peer_assignmetns_filename,
            parents=[assignments_folder])

        self.sut.set_gdrive_get_file_response(
            f"/{foldername}/{assignments_folder}/{peer_assignmetns_filename}",
            peer_assignments_file)

        peers = {
            'peer1': ['peer2']
        }

        # when:
        self.sut.write_peers_assignment(peers)

    def test_write_peers_assignment_when_no_folder(self):
        foldername = 'google_folder'
        assignments_folder = 'assignments_folder'
        assignments_file = 'assignments_peers_file'
        self.sut.set_gdrive_get_file_raise_exception(f'/{foldername}/{assignments_folder}/{assignments_file}')

        # when:
        with self.assertRaises(MissingGoogleDriveFolderException):
            self.sut.write_peers_assignment({})

    def test_write_peers_assignment_when_no_file(self):
        # when:
        with self.assertRaises(MissingGoogleDriveFileException):
            self.sut.write_peers_assignment({})

from unittest import TestCase

from evalytics.google_api import GmailAPI, FilesAPI

from tests.common.mocks import MockGmailService
from tests.common.mocks import MockDriveService, MockSheetsService

class FilesAPISut(FilesAPI, MockDriveService, MockSheetsService):
    'Inject mocks into FilesAPI dependencies'

class GmailAPISut(GmailAPI, MockGmailService):
    'Inject a mock into the GmailAPI dependency'

class TestGmailApi(TestCase):

    def test_send(self):
        user_id = 'any_user_id'
        message = 'any_message'
        sut = GmailAPISut()

        sut.send_message(user_id, message)

        calls = sut.get_send_calls()
        self.assertEqual(1, len(calls))
        self.assertEqual(user_id, calls[0]['user_id'])

class TestFilesAPI(TestCase):

    def setUp(self):
        self.sut = FilesAPISut()

    def test_create_drive_folder(self):
        folder_name = 'test folder'

        self.sut.create_folder(folder_name)

        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))
        self.assertIn('create_drive_folder', calls)

        call = calls['create_drive_folder'][0]
        self.assertIn('file_metadata', call)
        self.assertEqual(
            folder_name,
            call['file_metadata']['name'])

    def test_create_spreadsheet(self):
        folder_parent = 'parent'
        folder = {'id': 'new_parent_id'}
        filename = 'filename'

        self.sut.create_sheet(folder_parent, folder, filename)

        calls = self.sut.get_calls()
        self.assertEqual(2, len(calls))

        self.assertIn('create_spreadsheet', calls)
        self.assertIn('update_file_parent', calls)

        call = calls['create_spreadsheet'][0]
        self.assertIn('file_metadata', call)
        self.assertEqual(
            filename,
            call['file_metadata']['properties']['title'])

        call = calls['update_file_parent'][0]
        self.assertIn('file_id', call)
        self.assertIn('current_parent', call)
        self.assertIn('new_parent', call)
        self.assertEqual(
            filename,
            call['file_id'])
        self.assertEqual(
            folder_parent,
            call['current_parent'])
        self.assertEqual(
            'new_parent_id',
            call['new_parent'])

    def test_get_folder_when_not_exists(self):
        folder_name = 'name'
        self.sut.set_pages_requested(0)

        folder = self.sut.get_folder(folder_name)

        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))

        self.assertEqual(None, folder)

    def test_correct_number_executions_when_get_folder_and_exists(self):
        folder_name = 'my_folder'
        number_of_requests = 1
        self.sut.set_pages_requested(number_of_requests)
        self.sut.set_response_files([
            {
                'name': folder_name
            }, {
                'name': 'file2'
            }
        ])

        folder = self.sut.get_folder(folder_name)

        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))
        self.assertIn('list_files', calls)

        calls = calls['list_files']
        self.assertEqual(number_of_requests, len(calls))

        self.assertEqual(folder_name, folder['name'])

    def test_correct_query_when_get_folder(self):
        folder_name = 'name'
        self.sut.set_pages_requested(0)

        self.sut.get_folder(folder_name)

        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))
        calls = self.sut.get_calls()
        self.assertEqual(
            "mimeType='application/vnd.google-apps.folder'",
            calls['list_files'][0]['query']
        )

    def test_get_file_id_from_folder_when_not_exists(self):
        folder_id = 'id'
        filename = 'name'
        self.sut.set_pages_requested(0)

        folder = self.sut.get_file_id_from_folder(folder_id, filename)

        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))

        self.assertEqual(None, folder)

    def test_correct_query_when_get_file_id_from_folder(self):
        folder_id = 'id'
        filename = 'my_file'
        expected_query = "'%s' in parents" % folder_id
        self.sut.set_pages_requested(0)

        self.sut.get_file_id_from_folder(folder_id, filename)

        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))
        self.assertEqual(
            expected_query,
            calls['list_files'][0]['query']
        )

    def test_correct_fileid_when_get_file_id_from_folder_and_exists(self):
        folder_id = 'id'
        filename = 'my_file'
        expected_file_id = 'nice id'
        number_of_requests = 1
        self.sut.set_pages_requested(number_of_requests)
        self.sut.set_response_files([
            {
                'name': 'file1',
                'id': 'file1',
            }, {
                'name': filename,
                'id': expected_file_id,
            }
        ])

        file_id = self.sut.get_file_id_from_folder(folder_id, filename)

        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))
        self.assertEqual(
            expected_file_id,
            file_id
        )

    def test_get_file_rows(self):
        folder_name = 'my_folder'
        filename = 'filename'
        file_id = 'file_id'
        folder_id = 'folder_id'
        number_of_requests = 2
        self.sut.set_pages_requested(number_of_requests)
        self.sut.set_response_files([
            {
                'name': folder_name,
                'id': folder_id
            }, {
                'name': filename,
                'id': file_id
            }
        ])
        rows_range = 'A2::F4'

        self.sut.get_file_rows(folder_name, filename, rows_range)

        calls = self.sut.get_calls()
        print(calls)
        self.assertEqual(2, len(calls))
        self.assertIn('list_files', calls)

        self.assertEqual(2, len(calls['list_files']))
        self.assertIn('get_file_rows_from_folder', calls)

        call = calls['get_file_rows_from_folder'][0]
        self.assertEqual(file_id, call['spreadsheet_id'])

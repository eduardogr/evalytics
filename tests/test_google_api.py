from unittest import TestCase

from evalytics.google_api import GmailAPI, FilesAPI, DocsService, GoogleDrive
from evalytics.google_api import SheetsService, GmailService
from evalytics.models import GoogleFile, ReviewerResponse, EvalKind
from evalytics.exceptions import MissingGoogleDriveFolderException
from evalytics.exceptions import MissingGoogleDriveFileException
from evalytics.exceptions import GoogleApiClientHttpErrorException

from tests.common.mocks import RawSheetsServiceMock
from tests.common.mocks import RawGmailServiceMock
from tests.common.mocks import RawDocsServiceMock
from tests.common.mocks import RawGoogleServiceMock
from tests.common.mocks import MockGoogleService, MockGmailService
from tests.common.mocks import MockGoogleDrive, MockSheetsService
from tests.common.mocks import MockDocsService

class DocServiceSut(DocsService, MockGoogleService):
    'Inject a mock into the DocsService dependency'

class SheetsServiceSut(SheetsService, MockGoogleService):
    'Inject a mock into the SheetsService dependency'

class GmailServiceSut(GmailService, MockGoogleService):
    'Inject a mock into the GmailService dependency'

class GoogleDriveSut(GoogleDrive, MockGoogleService):
    'Inject a mock into the GoogleDrive dependency'

class FilesAPISut(
        FilesAPI,
        MockGoogleDrive,
        MockSheetsService,
        MockDocsService):
    'Inject mocks into FilesAPI dependencies'

class GmailAPISut(GmailAPI, MockGmailService):
    'Inject a mock into the GmailAPI dependency'

class TestGoogleDrive(TestCase):

    def setUp(self):
        self.sut = GoogleDriveSut()
        drive_service = RawGoogleServiceMock()
        self.sut.set_service(
            GoogleDrive.DRIVE_SERVICE_ID,
            GoogleDrive.DRIVE_SERVICE_VERSION,
            drive_service
        )

    def test_create_folder_ok(self):
        name = ''

        self.sut.create_folder(name)

    def test_gdrive_list_when_folder_no_exists(self):
        # when:
        with self.assertRaises(MissingGoogleDriveFolderException):
            self.sut.gdrive_list('/unexistent')

    #
    # TODO:
    # Improve mocks to build fixtures and make asserts about what's going on
    #

    # TODO
    def test_gdrive_list_when_for(self):
        # when:
        #self.sut.gdrive_list('/basefolder')
        pass

    # TODO
    def test_gdrive_list_when_for_none(self):
        # when:
        with self.assertRaises(MissingGoogleDriveFolderException):
            self.sut.gdrive_list('/something/unexistent')

    # TODO
    def test_gdrive_list_when_no_for(self):
        # when:
        self.sut.gdrive_list('/')

    def test_gdrive_get_file_when_incorrect_path(self):
        # when:
        google_file = self.sut.gdrive_get_file('/')

        # then:
        self.assertEqual(None, google_file)

    def test_gdrive_get_file_when_unexistent_file(self):
        # when:
        with self.assertRaises(MissingGoogleDriveFolderException):
            self.sut.gdrive_get_file('/unexistent/path/file')

    # TODO
    def test_gdrive_get_file_for(self):
        # when:
        #self.sut.gdrive_get_file('/existent/path/existent_file')
        pass

    # TODO
    def test_gdrive_get_file_for_none(self):
        pass

    # TODO
    def test_gdrive_get_file_no_for(self):
        pass

    def test_update_file_parent_ok(self):
        file_id = 'ID'
        current_parent = 'father'
        new_parent = 'i am your father'

        self.sut.update_file_parent(file_id, current_parent, new_parent)

    def test_list_files_ok(self):
        page_token = ''
        query = ''

        self.sut.list_files(page_token, query)

    def test_copy_file_ok(self):
        file_id = 'EFAWEF'
        new_filename = 'brand new file'

        self.sut.copy_file(file_id, new_filename)

    def test_create_permission_ok(self):
        document_id = 'ASDFASDF'
        role = 'comenter'
        email_address = 'myemail@email.com'

        self.sut.create_permission(document_id, role, email_address)


class TestSheetsService(TestCase):

    def setUp(self):
        self.sut = SheetsServiceSut()
        self.sut.set_service(
            SheetsService.SHEETS_SERVICE_ID,
            SheetsService.SHEETS_SERVICE_VERSION,
            RawSheetsServiceMock()
        )

    def test_create_spreadsheet_ok(self):
        file_metadata = {}
        self.sut.create_spreadsheet(file_metadata)

    def test_get_file_values_ok(self):
        spreadsheet_id = 'id'
        self.sut.get_file_values(spreadsheet_id, 'A1:D3')

    def test_get_file_values_ok_when_cached(self):
        spreadsheet_id = 'id'

        self.sut.get_file_values(spreadsheet_id, 'A1:D3')
        self.sut.get_file_values(spreadsheet_id, 'A1:D3')

        # TODO: do assertion for cache

    def test_update_file_values_ok(self):
        spreadsheet_id = 'id'
        rows_range = 'A3:D4'
        value_input_option = 'RAW'
        values = []
        self.sut.update_file_values(spreadsheet_id, rows_range, value_input_option, values)

class TestGmailService(TestCase):

    def setUp(self):
        self.sut = GmailServiceSut()
        self.sut.set_service(
            GmailService.GMAIL_SERVICE_ID,
            GmailService.GMAIL_SERVICE_VERSION,
            RawGmailServiceMock()
        )

    def test_send_email_ok(self):
        user_id = 'ME'
        body = 'jeje'
        self.sut.send_email(user_id, body)

class TestDocsService(TestCase):

    def setUp(self):
        self.sut = DocServiceSut()
        self.sut.set_service(
            DocsService.DOCS_SERVICE_ID,
            DocsService.DOCS_SERVICE_VERSION,
            RawDocsServiceMock()
        )

    def test_get_document_ok(self):
        document_id = 'ID'

        self.sut.get_document(document_id)

    def test_batch_update(self):
        document_id = 'ID'
        requests = []

        self.sut.batch_update(document_id, requests)

    def test_get_eval_report_style_tokens_has_tokens(self):
        style_tokens = self.sut.get_eval_report_style_tokens()

        self.assertEqual(4, len(style_tokens))
        self.assertIn('eval_title', style_tokens)
        self.assertIn('reviewer', style_tokens)
        self.assertIn('question', style_tokens)
        self.assertIn('answer', style_tokens)

    def test_get_delete_tokens_requests(self):
        delete_token_requests = self.sut.get_delete_tokens_requests()

        self.assertEqual(8, len(delete_token_requests))

    def test_get_eval_report_style_for_question(self):
        # given:
        kind = 'question'
        start_index = 0
        end_index = 0

        # when:
        style = self.sut.get_eval_report_style(kind, start_index, end_index)

        self.assertIn('updateTextStyle', style)

    def test_get_eval_report_style_for_reviewer(self):
        # given:
        kind = 'reviewer'
        start_index = 0
        end_index = 0

        # when:
        style = self.sut.get_eval_report_style(kind, start_index, end_index)

        self.assertIn('updateTextStyle', style)

    def test_get_eval_report_style_for_eval_title(self):
        # given:
        kind = 'eval_title'
        start_index = 0
        end_index = 0

        # when:
        style = self.sut.get_eval_report_style(kind, start_index, end_index)

        self.assertIn('updateTextStyle', style)

    def test_get_eval_report_style_for_answer(self):
        # given:
        kind = 'answer'
        start_index = 0
        end_index = 0

        # when:
        style = self.sut.get_eval_report_style(kind, start_index, end_index)

        self.assertEqual(None, style)

    def test_get_eval_report_style_when_no_defined_kind_exception_is_raised(self):
        # given:
        kind = 'whateverthinkthatNOTexist'
        start_index = 0
        end_index = 0

        with self.assertRaises(NotImplementedError):
            self.sut.get_eval_report_style(kind, start_index, end_index)

class TestGmailApi(TestCase):

    def test_send_message(self):
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
        self.sut.raise_exception_for_get_file_values_for_ids([])

    def tearDown(self):
        self.sut.clear_gdrive_list_fixture()
        self.sut.clear_gdrive_get_file_fixture()

    def test_create_folder(self):
        # given:
        folder_name = 'test folder'

        # when:
        self.sut.create_folder(folder_name)

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))
        self.assertIn('create_folder', calls)

        call = calls['create_folder'][0]
        self.assertIn('name', call)
        self.assertEqual(
            folder_name,
            call['name'])

    def test_create_spreadsheet(self):
        # given:
        folder_parent = 'parent'
        filename = 'filename'
        folder = GoogleFile(id='new_parent_id', name='folder', parents=[])

        # when:
        self.sut.create_sheet(folder_parent, folder, filename)

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(2, len(calls))

        self.assertIn('create_spreadsheet', calls)
        self.assertIn('update_file_parent', calls)

        call = calls['create_spreadsheet'][0]
        self.assertIn('filename', call)
        self.assertEqual(
            filename,
            call['filename'])

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
        # given:
        folder_name = 'name'
        self.sut.set_pages_requested(0)

        # when:
        folder = self.sut.get_folder(folder_name)

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))

        self.assertEqual(None, folder)

    def test_correct_number_executions_when_get_folder_and_exists(self):
        # given:
        folder_name = 'my_folder'
        self.sut.set_pages_requested(1)
        self.sut.set_response_files([
            GoogleFile(id='some id', name=folder_name, parents=[])
        ])

        # when:
        folder = self.sut.get_folder(folder_name)

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))
        self.assertIn('list_files', calls)

        self.assertEqual(folder_name, folder.name)

    def test_correct_query_when_get_folder(self):
        # given:
        folder_name = 'name'

        # when:
        self.sut.get_folder(folder_name)

        # when:
        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))
        self.assertIn('list_files', calls)

        self.assertEqual(
            GoogleDrive.QUERY_IS_FOLDER,
            calls['list_files'][0]['query']
        )

    def test_get_file_rows_from_folder(self):
        # given:
        foldername = 'my_folder'
        filename = 'filename'
        file_id = 'file_id'
        self.sut.set_gdrive_get_file_response(
            f"/{foldername}/{filename}",
            GoogleFile(id=file_id, name=filename, parents=[]))
        rows_range = 'A2::F4'

        # when:
        self.sut.get_file_rows_from_folder(foldername, filename, rows_range)

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(2, len(calls))

        self.assertIn('gdrive_get_file', calls)
        self.assertEqual(1, len(calls['gdrive_get_file']))
        self.assertIn('get_file_values', calls)
        self.assertEqual(1, len(calls['get_file_values']))

        call = calls['get_file_values'][0]
        self.assertEqual(file_id, call['spreadsheet_id'])

    def test_get_file_rows_from_folder_when_missing_google_folder_exception(self):
        # given:
        foldername = 'my_folder'
        filename = 'filename'
        rows_range = 'A2::F4'
        self.sut.set_gdrive_get_file_raise_exception(f"/{foldername}/{filename}")

        # when:
        with self.assertRaises(MissingGoogleDriveFolderException):
            self.sut.get_file_rows_from_folder(foldername, filename, rows_range)

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))
        self.assertIn('gdrive_get_file', calls)
        self.assertEqual(1, len(calls['gdrive_get_file']))

    def test_get_file_rows_from_folder_when_missing_google_file_exception(self):
        # given:
        foldername = 'my_folder'
        filename = 'filename'
        self.sut.set_gdrive_get_file_response(
            f"/{foldername}/{filename}",
            None)
        rows_range = 'A2::F4'

        # when:
        with self.assertRaises(MissingGoogleDriveFileException):
            self.sut.get_file_rows_from_folder(foldername, filename, rows_range)

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))
        self.assertIn('gdrive_get_file', calls)
        self.assertEqual(1, len(calls['gdrive_get_file']))

    def test_get_file_rows_when_ok(self):
        # given:
        file_id = 'file_id'
        rows_range = 'A2::F4'

        # when:
        self.sut.get_file_values(file_id, rows_range)

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))
        self.assertIn('get_file_values', calls)
        self.assertEqual(1, len(calls['get_file_values']))

    def test_get_file_rows_when_http_error(self):
        # given:
        file_id = 'file_id'
        rows_range = 'A2::F4'
        self.sut.raise_exception_for_get_file_values_for_ids([file_id])

        # when:
        with self.assertRaises(GoogleApiClientHttpErrorException):
            self.sut.get_file_values(file_id, rows_range)

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(0, len(calls))

    def test_update_file_values_when_ok(self):
        # given:
        file_id = 'file_id'
        rows_range = 'A2::F4'

        # when:
        self.sut.update_file_values(file_id, rows_range, 'RAW', [])

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))
        self.assertIn('update_file_values', calls)
        self.assertEqual(1, len(calls['update_file_values']))

    def test_insert_eval_report_in_document_when_no_evaluations_then_empty_file(self):
        # given:
        eval_process_id = ''
        document_id = 'ID'
        reviewee = ''
        reviewee_evaluations = {}

        # when:
        self.sut.insert_eval_report_in_document(
            eval_process_id,
            document_id,
            reviewee,
            reviewee_evaluations)

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(2, len(calls))
        self.assertIn('batch_update', calls)
        self.assertIn('get_document', calls)

    def test_insert_eval_report_in_document_when_no_eval_response(self):
        # given:
        eval_process_id = ''
        document_id = 'ID'
        reviewee = ''
        reviewee_evaluations = [
            ReviewerResponse(
                reviewee=reviewee,
                reviewer=reviewee,
                eval_kind=EvalKind.PEER_MANAGER,
                eval_response=[],
                filename="Self evaluation",
                line_number=10
            )
        ]

        # when:
        self.sut.insert_eval_report_in_document(
            eval_process_id,
            document_id,
            reviewee,
            reviewee_evaluations)

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(2, len(calls))
        self.assertIn('batch_update', calls)
        self.assertIn('get_document', calls)

    def test_insert_eval_report_in_document(self):
        # given:
        eval_process_id = ''
        document_id = 'ID'
        reviewee = ''
        reviewee_evaluations = [
            ReviewerResponse(
                reviewee=reviewee,
                reviewer=reviewee,
                eval_kind=EvalKind.SELF,
                eval_response=[('Do you know hot to dance?', 'Of course!')],
                filename="Report by direct report",
                line_number=10
            )
        ]

        # when:
        self.sut.insert_eval_report_in_document(
            eval_process_id,
            document_id,
            reviewee,
            reviewee_evaluations)

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(2, len(calls))
        self.assertIn('batch_update', calls)
        self.assertIn('get_document', calls)

    def test_empty_document_when_empty_file(self):
        # given:
        document_id = 'ID'

        # when:
        self.sut.empty_document(document_id)

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(1, len(calls))
        self.assertIn('get_document', calls)

    def test_empty_document_when_document_exist(self):
        # given:
        document_id = 'ID'
        self.sut.set_start_index(4)
        self.sut.set_end_index(0)

        # when:
        self.sut.empty_document(document_id)

        # then:
        calls = self.sut.get_calls()
        self.assertEqual(2, len(calls))
        self.assertIn('get_document', calls)
        self.assertIn('batch_update', calls)

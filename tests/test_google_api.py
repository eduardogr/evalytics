from unittest import TestCase

from googledrive.exceptions import GoogleApiClientHttpErrorException

from evalytics.google_api import GmailAPI, FilesAPI, DocsService, GoogleDrive
from evalytics.google_api import SheetsService, GmailService
from evalytics.models import ReviewerResponse, EvalKind

from tests.common.mocks import RawGmailServiceMock
from tests.common.mocks import RawDocsServiceMock
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

    def test_get_delete_tokens_requests(self):
        # given:
        tokens = {
            1: {'start': 'si', 'end': 'no'},
            2: {'start': 'si', 'end': 'no'},
            3: {'start': 'si', 'end': 'no'},
            4: {'start': 'si', 'end': 'no'}
        }

        # when:
        delete_token_requests = self.sut.get_delete_tokens_requests(tokens)

        # then:
        self.assertEqual(8, len(delete_token_requests))


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

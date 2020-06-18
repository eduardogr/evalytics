
import tornado.web

from evalytics.config import Config, ConfigReader
from evalytics.models import Reviewer, GoogleSetup, GoogleFile
from evalytics.communications_channels import CommunicationChannelFactory
from evalytics.communications_channels import GmailChannel
from evalytics.storages import GoogleStorage, StorageFactory
from evalytics.forms import FormsPlatformFactory, GoogleForms
from evalytics.google_api import GoogleAPI
from evalytics.google_api import GmailService, DriveService
from evalytics.google_api import SheetsService, DocsService
from evalytics.usecases import SetupUseCase, GetReviewersUseCase
from evalytics.usecases import SendEvalUseCase
from evalytics.adapters import EmployeeAdapter, ReviewerAdapter
from evalytics.mappers import Mapper
from evalytics.filters import ReviewerResponseFilter

from client import EvalyticsRequests
from client import EvalyticsClient
from client import FileManager

from tests.common.employees import employees_collection

class MockEmployeeAdapter(EmployeeAdapter):

    def __init__(self):
        self.employees_by_manager = {}

    def build_reviewers(self, employees, peers_assignment, forms):
        return employees

    def build_message(self, message, reviewer: Reviewer):
        return ""

    def get_employees_by_manager(self, employees):
        return self.employees_by_manager

    def set_employees_by_manager(self, employees_by_manager):
        self.employees_by_manager = employees_by_manager

    def get_employee_managers(self, employees, employee_uid):
        return []

class MockReviewerAdapter(ReviewerAdapter):

    def get_status_from_responses(self, reviewers, responses):
        return [], [], []

class MockDriveService(DriveService):

    def __init__(self):
        self.calls = {}
        self.response_files = []
        self.pages_requested = 0

    def create_drive_folder(self, file_metadata):
        self.__update_calls(
            'create_drive_folder',
            params={
                'file_metadata': file_metadata
            }
        )
        return {
            'folder': file_metadata
        }

    def update_file_parent(self, file_id, current_parent, new_parent):
        self.__update_calls(
            'update_file_parent',
            params={
                'file_id': file_id,
                'current_parent': current_parent,
                'new_parent': new_parent,
            }
        )

    def list_files(self, page_token: str, query: str):
        self.__update_calls(
            'list_files',
            params={
                'page_token': page_token,
                'query': query,
            }
        )
        if self.pages_requested > 0:
            self.pages_requested -= 1
            return {
                'files': self.response_files,
                'nextPageToken': 'pagetoken::{}'.format(self.pages_requested)
            }

        return {
            'files': [],
            'nextPageToken': None
        }

    def copy_file(self, file_id, new_filename):
        return "ID"

    def create_permission(self, document_id: str, role: str, email_address):
        self.__update_calls(
            'create_permission',
            params={
                'document_id': document_id,
                'role': role,
                'email_address': email_address
            }
        )
        return

    def get_calls(self):
        return self.calls

    def set_pages_requested(self, pages_requested):
        self.pages_requested = pages_requested

    def set_response_files(self, response_files):
        self.response_files = response_files

    def __update_calls(self, function, params):
        current_call_number = 0

        if function in self.calls:
            sorted_keys = sorted(self.calls[function].keys())
            sorted_keys.reverse()
            current_call_number = sorted_keys[0] + 1

            self.calls[function].update({
                current_call_number: params
            })
        else:
            self.calls.update({
                function: {
                    current_call_number: params
                }
            })


class MockSheetsService(SheetsService):

    def __init__(self):
        self.calls = {}

    def create_spreadsheet(self, file_metadata):
        self.__update_calls(
            'create_spreadsheet',
            params={
                'file_metadata': file_metadata
            }
        )
        return {
            'spreadsheetId': file_metadata['properties']['title']
        }

    def get_file_values(self, spreadsheet_id, rows_range):
        self.__update_calls(
            'get_file_rows_from_folder',
            params={
                'spreadsheet_id': spreadsheet_id,
                'rows_range': rows_range,   
            }
        )
        return {
            'values': ['whatever']
        }

    def get_calls(self):
        return self.calls

    def __update_calls(self, function, params):
        current_call_number = 0

        if function in self.calls:
            sorted_keys = sorted(self.calls[function].keys())
            sorted_keys.reverse()
            current_call_number = sorted_keys[0] + 1

            self.calls[function].update({
                current_call_number: params
            })
        else:
            self.calls.update({
                function: {
                    current_call_number: params
                }
            })

class MockDocsService(DocsService):

    def __init__(self):
        self.calls = {}

    def get_document(self, document_id):
        self.__update_calls(
            'get_document',
            params={
                'document_id': document_id,
            }
        )
        return {
            'body': {
                'content': [
                    {
                        'paragraph': {
                            'elements': [
                                {
                                    'horizontalRule': {},
                                    'endIndex': 99
                                }
                            ]
                        }
                    }
                ]
            }
        }

    def batch_update(self, document_id, requests):
        self.__update_calls(
            'batch_update',
            params={
                'document_id': document_id,
                'requests': requests
            }
        )

    def get_calls(self):
        return self.calls

    def __update_calls(self, function, params):
        current_call_number = 0

        if function in self.calls:
            sorted_keys = sorted(self.calls[function].keys())
            sorted_keys.reverse()
            current_call_number = sorted_keys[0] + 1

            self.calls[function].update({
                current_call_number: params
            })
        else:
            self.calls.update({
                function: {
                    current_call_number: params
                }
            })

class MockGmailService(GmailService):

    def __init__(self):
        self.send_calls = {}

    def send_email(self, user_id, body):
        current_call_number = 0

        if len(self.send_calls) > 0:
            sorted_keys = sorted(self.send_calls.keys())
            sorted_keys.reverse()
            current_call_number = sorted_keys[0] + 1

        self.send_calls.update({
            current_call_number: {
                'user_id': user_id,
                'body': body
            }
        })

        return body

    def get_send_calls(self):
        return self.send_calls

class MockGoogleAPI(GoogleAPI,
                    MockDriveService,
                    MockSheetsService,
                    MockDocsService,
                    MockGmailService):

    def __init__(self):
        self.response = []
        self.files_from_folder_response = []
        self.file_rows_by_id_response = {}
        self.folder = None
        self.folder_from_folder = None
        self.fileid_by_name = {}
        self.send_message_calls = {}

    def get_file_rows_from_folder(self, foldername: str, filename: str, rows_range: str):
        return self.response

    def get_file_rows(self, file_id: str, rows_range: str):
        return self.file_rows_by_id_response.get(file_id, [])

    def get_files_from_folder(self, folder_id):
        return self.files_from_folder_response

    def get_folder(self, name: str):
        return self.folder

    def get_folder_from_folder(self, foldername, parent_foldername):
        return self.folder_from_folder

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

    def create_sheet(self, folder_parent: str, folder, filename: str):
        spreasheet_id = filename
        self.set_fileid_by_name(folder['id'], spreasheet_id, spreasheet_id)
        return spreasheet_id

    def send_message(self, user_id, message):
        current_call_number = 0

        if len(self.send_message_calls) > 0:
            sorted_keys = sorted(self.send_message_calls.keys())
            sorted_keys.reverse()
            current_call_number = sorted_keys[0] + 1

        self.send_message_calls.update({
            current_call_number: {
                'user_id': user_id,
                'message': message
            }
        })

    def insert_eval_report_in_document(self,
                                       eval_process_id,
                                       document_id,
                                       reviewee,
                                       reviewee_evaluations):
       return

    def add_comenter_permission(self, document_id, emails):
        return

    def get_send_message_calls(self):
        return self.send_message_calls

    def set_file_rows_response(self, response):
        self.response = response

    def set_file_rows_by_id(self, file_id, response):
        self.file_rows_by_id_response.update({
            file_id: response
        })

    def set_files_from_folder_response(self, response):
        self.files_from_folder_response = response

    def set_folder_from_folder(self, folder):
        self.folder_from_folder = folder

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
        self.storage_provider = ""
        self.communications_provider = ""
        self.forms_platform_provider = ""

    def read_storage_provider(self):
        return self.storage_provider

    def read_communication_channel_provider(self):
        return self.communications_provider

    def read_forms_platform_provider(self):
        return self.forms_platform_provider

    def read_mail_subject(self):
        return "important subject"

    def reminder_mail_subject(self):
        return "reminder subject"

    def read_google_folder(self):
        return "google_folder"

    def read_assignments_folder(self):
        return "assignments_folder"

    def read_assignments_manager_forms_folder(self):
        return "assignments_manager_forms_folder("

    def read_google_orgchart(self):
        return "google_orgchart"

    def read_google_form_map(self):
        return "google_form_map"

    def read_assignments_peers_file(self):
        return "assignments_peers_file"

    def read_needed_spreadsheets(self):
        return self.needed_spreadsheets

    def read_google_responses_folder(self):
        return "form_responses_folder"

    def read_company_domain(self):
        return "company.com"

    def read_company_number_of_employees(self):
        return 1000

    def read_google_eval_report_template_id(self):
        return "ID::ADSFASDFRE"

    def read_google_eval_report_prefix_name(self):
        return "PREFIX: "

    def set_needed_spreadhseets(self, needed_spreadhseets):
        self.needed_spreadsheets = needed_spreadhseets

    def set_storage_provider(self, provider):
        self.storage_provider = provider

    def set_communications_provider_provider(self, provider):
        self.communications_provider = provider

    def set_forms_platform_provider(self, provider):
        self.forms_platform_provider = provider

class MockStorageFactory(StorageFactory, MockConfig):

    storage_impl = None

    def get_storage(self):
        return self.storage_impl

    def set_storage(self, impl):
        self.storage_impl = impl

class MockFormsPlatformFactory(FormsPlatformFactory, MockConfig):

    forms_platform_impl = None

    def get_forms_platform(self):
        return self.forms_platform_impl

    def set_forms_platform(self, impl):
        self.forms_platform_impl = impl

class MockGoogleForms(GoogleForms):

    def __init__(self):
        self.evaluations_response = {}

    def get_responses(self):
        return {}

    def get_evaluations(self):
        return self.evaluations_response

    def set_evaluations_response(self, response):
        self.evaluations_response = response

class MockGoogleStorage(GoogleStorage):

    def __init__(self):
        self.evaluations_raise_exception_by_reviewee = []

    def setup(self):
        mock_fileid = 'mockid'
        mock_filename = 'mockfolder'
        folder = GoogleFile(name=mock_filename, id=mock_fileid)
        orgchart = GoogleFile(name=mock_filename, id=mock_fileid)
        return GoogleSetup(folder=folder, files=[orgchart])

    def get_employees(self):
        return {
            'em_email': employees_collection().get('em_email'),
            'manager_em': employees_collection().get('manager_em'),
        }

    def get_forms(self):
        return {}

    def generate_eval_reports(self,
                              dry_run,
                              eval_process_id,
                              reviewee,
                              reviewee_evaluations,
                              employee_managers):
        if reviewee in self.evaluations_raise_exception_by_reviewee:
            raise Exception

        return []

    def get_evaluations_will_raise_exception_for_reviewee(self, reviewee):
        self.evaluations_raise_exception_by_reviewee.append(reviewee)

class MockCommunicationChannelFactory(CommunicationChannelFactory, MockConfig):

    impl = None

    def get_communication_channel(self):
        return self.impl

    def set_communication_channel(self, impl):
        self.impl = impl

class MockGmailChannel(GmailChannel):

    def __init__(self):
        self.raise_exception_for_reviewers = []

    def add_raise_exception_for_reviewer(self, reviewer_uid: str):
        self.raise_exception_for_reviewers.append(reviewer_uid)

    def send_communication(self, reviewer: Reviewer, mail_subject: str, data):
        if reviewer.uid in self.raise_exception_for_reviewers:
            raise Exception("MockCommunicationsProvider was asked to throw this exception")
        return

class MockConfigReader(ConfigReader):

    def read(self, filename: str = ''):
        return {
            'providers': {
                'storage': 'storage-provider',
                'communication_channel': 'comm-provider',
                'forms_platform': 'form-provider',
            },
            'gmail_provider': {
                'mail_subject': 'this is the mail subject',
                'reminder_mail_subject': 'reminder subject'
            },
            'google_drive_provider': {
                'folder': 'mock_folder',
                'form_responses_folder': 'mock_tests_folder',
                'assignments_folder': 'mock_assignments_folder',
                'assignments_manager_forms_folder': 'mock_man_ssignments_folder',
                'org_chart': 'mock_orgchart',
                'form_map': 'mock_formmap',
                'assignments_peers_file': 'assignments_peers_file',
                'eval_report_template_id': 'ID',
                'eval_report_prefix_name': 'Prefix'
            },
            'company': {
                'domain': 'mock_domain.com',
                'number_of_employees': 20,
            }
        }

    def get(self, key, section):
        return self.read()[key][section]

class MockMapper(Mapper):

    def __init__(self):
        self.reviewers = []

    def set_reviewers(self, reviewers):
        self.reviewers = reviewers

    def json_to_reviewers(self, json_reviewers):
        return self.reviewers

class MockReviewerResponseFilter(ReviewerResponseFilter):

    def filter_reviewees(self,
                         reviewee_evaluations,
                         employees,
                         area,
                         managers,
                         allowed_uids):
        return reviewee_evaluations

class SendEvalUseCaseMock(
        SendEvalUseCase,
        MockCommunicationChannelFactory,
        MockEmployeeAdapter,
        MockConfig):

    def __init__(self):
        self.evals_sent = []
        self.evals_not_sent = []

    def set_response(self, evals_sent, evals_not_sent):
        self.evals_sent = evals_sent
        self.evals_not_sent = evals_not_sent

    def send_eval(self, reviewers, is_reminder=False):
        return self.evals_sent, self.evals_not_sent

class GetReviewersUseCaseMock(GetReviewersUseCase, MockStorageFactory, MockEmployeeAdapter):

    def __init__(self):
        self.response = {}

    def set_get_reviewers(self, response):
        self.response = response

    def get_reviewers(self):
        return self.response

class SetupUseCaseMock(SetupUseCase, MockStorageFactory):

    def __init__(self):
        self.response = {}

    def set_setup(self, setup):
        self.response = setup

    def setup(self):
        return self.response

class RequestHandlerMock(tornado.web.RequestHandler):
    
    def __init__(self):
        self.finish_data = {}
        self.arguments = {}

    def data_received(self):
        pass

    def set_argument(self, argument: str, value: str):
        self.arguments.update({
            argument: value
        })

    def get_argument(self, argument: str, default: str, strip):
        return self.arguments.get(argument)

    def finish(self, data):
        self.finish_data = data

    def get_finish_data(self):
        return self.finish_data

#
# client.py mocks
#

class MockFile:

    def readlines(self):
        return []

    def close(self):
        return

class MockFileManager(FileManager):

    def open(self, filename: str, mode: str):
        return MockFile()

class MockEvalyticsRequests(EvalyticsRequests):

    BASE_URL = "mock:8080"

    def __init__(self):
        self.calls = {}
        self.setup_response = {}
        self.reviewers_response = {}
        self.status_response = {}
        self.evaldelivery_response = {}
        self.evalreports_response = {}

    def set_setup_response(self, response):
        self.setup_response = response

    def setup(self):
        self.update_calls('setup')
        return True, self.setup_response

    def set_reviewers_response(self, response):
        self.reviewers_response = response

    def reviewers(self):
        self.update_calls('reviewers')
        return True, self.reviewers_response

    def set_status_response(self, response):
        self.status_response = response

    def status(self):
        self.update_calls('status')
        return True, self.status_response

    def set_evaldelivery_response(self, response):
        self.evaldelivery_response = response

    def evaldelivery(self, json_reviewers, is_reminder: bool = False):
        self.update_calls('evaldelivery')
        return True, self.evaldelivery_response

    def set_evalreports_response(self, response):
        self.evalreports_response = response

    def evalreports(self, eval_process_id, dry_run, uids):
        self.update_calls('evalreports')
        return True, self.evalreports_response

    def get_data_response(self, response):
        self.update_calls('get_data_response')

    def update_calls(self, method):
        calls = 0
        if method in self.calls.keys():
            calls = self.calls[method]
        self.calls.update({
            method:(calls + 1)
        })

    def get_calls(self):
        return self.calls

class MockEvalyticsClient(EvalyticsClient):

    def __init__(self):
        self.calls = {}
        self.show_stats = False
        self.dry_run = False

    def print_reviewers(self, show_stats=False):
        self.update_calls('print_reviewers')
        self.show_stats = show_stats

    def print_status(self):
        self.update_calls('print_status')

    def print_inconsistent_files_status(self):
        self.update_calls('print_inconsistent_files_status')

    def post_setup(self):
        self.update_calls('post_setup')

    def send_eval(self, whitelist=None, dry_run: bool = False):
        self.update_calls('send_eval')
        self.dry_run = dry_run

    def retry_send_eval(self, dry_run: bool = False):
        self.update_calls('retry_send_eval')
        self.dry_run = dry_run

    def whitelist_send_eval(self, dry_run: bool = False):
        self.update_calls('whitelist_send_eval')
        self.dry_run = dry_run

    def send_reminder(self, whitelist=None, dry_run: bool = False):
        self.update_calls('send_reminder')
        self.dry_run = dry_run

    def retry_send_reminder(self, dry_run: bool = False):
        self.update_calls('retry_send_reminder')
        self.dry_run = dry_run

    def whitelist_send_reminder(self, dry_run: bool = False):
        self.update_calls('whitelist_send_reminder')
        self.dry_run = dry_run

    def generate_reports(self, eval_process_id, whitelist=None, dry_run: bool = False):
        self.update_calls('generate_reports')
        self.dry_run = dry_run

    def whitelist_generate_reports(self, eval_process_id, dry_run: bool = False):
        self.update_calls('whitelist_generate_reports')
        self.dry_run = dry_run

    def help(self, command):
        self.update_calls('help')

    def update_calls(self, method):
        calls = 0
        if method in self.calls.keys():
            calls = self.calls[method]
        self.calls.update({
            method:(calls + 1)
        })

    def get_calls(self):
        return self.calls

    def get_show_stats(self):
        return self.show_stats

    def get_dry_run(self):
        return self.dry_run

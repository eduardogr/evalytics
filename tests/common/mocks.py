
from googleapiclient.errors import HttpError

from evalytics.config import Config, ConfigReader
from evalytics.models import GoogleFile
from evalytics.models import Reviewer, CommunicationKind, PeersAssignment
from evalytics.communications_channels import CommunicationChannelFactory
from evalytics.communications_channels import GmailChannel, SlackClient
from evalytics.storages import GoogleStorage, StorageFactory
from evalytics.forms import FormsPlatformFactory, GoogleForms
from evalytics.google_api import GoogleAPI, GoogleService
from evalytics.google_api import GmailService, DriveService
from evalytics.google_api import SheetsService, DocsService
from evalytics.usecases import GetReviewersUseCase
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

class MockGoogleService(GoogleService):

    __services_by_id = {}

    def get_service(self, service_id, service_version):
        return self.__services_by_id[service_id][service_version]

    def set_service(self, service_id, service_version, service):
        if service_id not in self.__services_by_id:
            self.__services_by_id.update({
                service_id: {}
            })

        if service_version not in self.__services_by_id[service_id]:
            self.__services_by_id[service_id].update({
                service_version: None
            })

        self.__services_by_id[service_id][service_version] = service

class RawSheetsServiceMock:

    def spreadsheets(self):
        class Spreadsheets:
            def create(self, body, fields):
                class Create:
                    def execute(self):
                        return {}
                return Create()

            def values(self):
                class Values:
                    def get(self, spreadsheetId, range):
                        class Get:
                            def execute(self):
                                return {
                                    'values': ['something']
                                }
                        return Get()

                    def update(
                            self,
                            spreadsheetId,
                            range,
                            valueInputOption,
                            body):
                        class Update:
                            def execute(self):
                                return {
                                    'values': []
                                }
                        return Update()
                return Values()

        return Spreadsheets()

class RawDriveServiceMock:

    def files(self):
        class Files:
            def create(self, body, fields):
                class Create:
                    def execute(self):
                        return {}
                return Create()

            def update(self, fileId, addParents, removeParents):
                class Update:
                    def execute(self):
                        return {}
                return Update()

            def list(self, q, pageSize, spaces, corpora, fields, pageToken):
                class List:
                    def execute(self):
                        return {
                            'files': [{
                                'name': '',
                                'id': ''
                            }]
                        }
                return List()

            def copy(self, fileId, body):
                class Copy:
                    def execute(self):
                        return {}
                return Copy()

        return Files()

    def permissions(self):
        class Permissions:
            def create(self, fileId, body):
                class Create:
                    def execute(self):
                        return {}
                return Create()
        return Permissions()

class RawGmailServiceMock:

    def users(self):
        class Users:
            def messages(self):
                class Messages:
                    def send(self, userId, body):
                        class Execute:
                            def execute(self):
                                return
                        return Execute()
                return Messages()
        return Users()

class RawDocsServiceMock:

    def documents(self):
        class Documents:
            def get(self, documentId):
                class Execute:
                    def execute(self):
                        return
                return Execute()

            def batchUpdate(self, documentId, body):
                class Execute:
                    def execute(self):
                        return
                return Execute()

        return Documents()

class MockDriveService(DriveService):

    def __init__(self):
        self.calls = {}
        self.response_files = []
        self.pages_requested = 0
        self.get_file_response = {}
        self.get_files_response = {}

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

    def get_file(self, query: str, filename):
        self.__update_calls(
            'get_file',
            params={
                'query': query,
                'filename': filename,
            }
        )
        return self.get_file_response.get(filename, None)

    def get_files(self, query: str):
        self.__update_calls(
            'get_files',
            params={
                'query': query,
            }
        )
        return self.get_files_response.get(query, None)

    def get_calls(self):
        return self.calls

    def set_pages_requested(self, pages_requested):
        self.pages_requested = pages_requested

    def set_get_file_response(self, filename, response):
        self.get_file_response.update({
            filename: response
        })

    def set_get_files_response(self, query, response):
        self.get_files_response.update({
            query: response
        })

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
        self.__get_file_values_will_raise_exception = []

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
        if spreadsheet_id in self.__get_file_values_will_raise_exception:
            content = '{"error": {"code": 429,"message": "this is a test error message","status": 429,"details": []}}'
            raise HttpError(resp='', content=bytes(content, 'utf-8'))

        self.__update_calls(
            'get_file_values',
            params={
                'spreadsheet_id': spreadsheet_id,
                'rows_range': rows_range,
            }
        )
        return {
            'values': ['whatever']
        }

    def update_file_values(self, spreadsheet_id, rows_range, value_input_option, values):
        self.__update_calls(
            'update_file_values',
            params={
                'spreadsheet_id': spreadsheet_id,
                'rows_range': rows_range,
                'value_input_option': value_input_option,
                'values': values,
            }
        )
        return {
            'values': ['whatever']
        }

    def raise_exception_for_get_file_values_for_ids(self, spreadsheet_collection):
        self.__get_file_values_will_raise_exception = spreadsheet_collection

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

    end_index = 99
    start_index = 1

    def __init__(self):
        self.calls = {}
        self.end_index = 99
        self.start_index = 1

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
                                    'endIndex': self.end_index,
                                    'startIndex': self.start_index
                                },
                                {
                                    'textRun': {
                                        'content': 'i am content'
                                    },
                                    'horizontalRule': {},
                                    'endIndex': self.end_index,
                                    'startIndex': self.start_index
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

    def set_end_index(self, index):
        self.end_index = index

    def set_start_index(self, index):
        self.start_index = index

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

class MockSlackClient(SlackClient):

    def __init__(self):
        self.chat_post_message_calls = {}

    def chat_post_message(
            self,
            token,
            channel,
            blocks,
            as_user):
        current_call_number = 0

        if len(self.chat_post_message_calls) > 0:
            sorted_keys = sorted(self.chat_post_message_calls.keys())
            sorted_keys.reverse()
            current_call_number = sorted_keys[0] + 1

        self.chat_post_message_calls.update({
            current_call_number: {
                'token': token,
                'channel': channel,
                'blocks': blocks,
                'as_user': as_user,
            }
        })

    def get_chat_post_message_calls(self):
        return self.chat_post_message_calls

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

    def update_file_rows(self, file_id: str, rows_range: str, value_input_option: str, values):
        return

    def get_files_from_folder(self, folder_id):
        return self.files_from_folder_response

    def get_folder(self, name: str):
        return self.folder

    def get_folder_from_folder(self, foldername, parent_foldername):
        return self.folder_from_folder

    def create_folder(self, name: str):
        folder = GoogleFile(
            id='folder_id',
            name='name',
            parents=['folders_parent']
        )
        self.set_folder(folder)
        return self.folder

    def get_file_id_from_folder(self, folder_id: str, filename: str):
        if folder_id in self.fileid_by_name:
            if filename in self.fileid_by_name[folder_id]:
                return self.fileid_by_name[folder_id][filename]
        return None

    def create_sheet(self, folder_parent: str, folder, filename: str):
        spreasheet_id = filename
        self.set_fileid_by_name(folder.id, spreasheet_id, spreasheet_id)
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

    def empty_document(self, document_id):
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
        if folder_id not in self.fileid_by_name:
            self.fileid_by_name.update({
                folder_id: {}
            })

        self.fileid_by_name.get(folder_id).update({filename: fileid})


class MockConfigReader(ConfigReader):

    def read(self, filename: str = ''):
        return {
            'eval_process': {
                'id': 'eval_process_id',
                'due_date': 'eval_process_due_date',
                'feature_disabling': {
                    'add_comenter_to_eval_reports': False
                }
            },
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
                'responses_files_range': 'A1:A1',
                'assignments_folder': 'mock_assignments_folder',
                'assignments_manager_forms_folder': 'mock_man_ssignments_folder',
                'org_chart': 'mock_orgchart',
                'org_chart_range': 'A1:A1',
                'form_map': 'mock_formmap',
                'form_map_range': 'A1:A1',
                'assignments_peers_file': 'assignments_peers_file',
                'assignments_peers_range': 'A1:A1',
                'eval_reports_folder': 'eval_reports_folder',
                'eval_report_template_id': 'ID',
                'file_prefixes': {
                    'manager_eval_by_report': 'Manager Evaluation By Report',
                    'report_eval_by_manager': 'Report Evaluation By Manager',
                    'peer_eval_by_peer': 'Peer Evaluation By Peer',
                    'self_eval': 'Self Evaluation',
                    'eval_report': 'Prefix'
                }
            },
            'slack_provider': {
                'token': 'TOKEN::TOKEN',
                'is_direct_message': True,
                'params': {
                    'text': "{}",
                    'channel': "@{}",
                    'as_user': True
                },
                'users_map': {}
            },
            'company': {
                'domain': 'mock_domain.com',
                'number_of_employees': 20,
            }
        }

    def get(self, key, section):
        return self.read()[key][section]

class MockConfig(Config, MockConfigReader):

    company_number_of_employees = 1000
    is_add_comenter_to_evals_reports_enabled = False

    def __init__(self):
        super().__init__()
        self.company_number_of_employees = 1000
        self.needed_spreadsheets = []
        self.storage_provider = ""
        self.communications_provider = ""
        self.forms_platform_provider = ""
        self.response_slack_message_is_direct = None
        self.slack_users_map = []
        self.is_add_comenter_to_evals_reports_enabled = False

    def read_eval_process_id(self):
        return 'EVAL_PROCESS_ID'

    def read_eval_process_due_date(self):
        return 'DUE_DATE'

    def read_is_add_comenter_to_eval_reports_enabled(self):
        return self.is_add_comenter_to_evals_reports_enabled

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

    def read_google_orgchart_range(self):
        return "A1:A1"

    def read_google_form_map(self):
        return "google_form_map"

    def read_google_form_map_range(self):
        return "A1:A1"

    def read_assignments_peers_file(self):
        return "assignments_peers_file"

    def read_assignments_peers_range(self):
        return "A1:A1"

    def read_google_responses_folder(self):
        return "form_responses_folder"

    def read_google_responses_files_range(self):
        return "A1:A1"

    def read_company_domain(self):
        return "company.com"

    def read_company_number_of_employees(self):
        return self.company_number_of_employees

    def read_eval_reports_folder(self):
        return "eval_reports_folder"

    def read_google_eval_report_template_id(self):
        return "ID::ADSFASDFRE"

    def read_google_eval_report_prefix(self):
        return "PREFIX: "

    def read_google_manager_eval_by_report_prefix(self):
        return "MANAGER EVAL BY REPORT"

    def read_google_report_eval_by_manager_prefix(self):
        return "REPORT EVAL BY MANAGER"

    def read_google_peer_eval_by_peer_prefix(self):
        return "PEER EVAL BY PEER"

    def read_google_self_eval_prefix(self):
        return "SELF EVAL"

    def set_is_add_comenter_to_evals_reports_enabled(self, is_enabled: bool):
        self.is_add_comenter_to_evals_reports_enabled = is_enabled

    def get_slack_token(self):
        return "TOKEN::TOKEN"

    def get_slack_text_param(self):
        return "This is an incredible text"

    def get_slack_channel_param(self):
        return "@{}"

    def slack_message_is_direct(self):
        return self.response_slack_message_is_direct

    def slack_message_as_user_param(self):
        return True

    def get_slack_users_map(self):
        return self.slack_users_map

    def set_company_number_of_employees(self, company_number_of_employees):
        self.company_number_of_employees = company_number_of_employees

    def set_needed_spreadhseets(self, needed_spreadhseets):
        self.needed_spreadsheets = needed_spreadhseets

    def set_storage_provider(self, provider):
        self.storage_provider = provider

    def set_communications_provider_provider(self, provider):
        self.communications_provider = provider

    def set_forms_platform_provider(self, provider):
        self.forms_platform_provider = provider

    def set_slack_message_is_direct(self, slack_message_is_direct):
        self.response_slack_message_is_direct = slack_message_is_direct

    def set_slack_users_map(self, users_map):
        self.slack_users_map = users_map

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
        self.peers_assignment = PeersAssignment({}, [])

    def get_peers_assignment(self):
        return self.peers_assignment

    def get_responses(self):
        return {}

    def get_evaluations(self):
        return self.evaluations_response

    def set_evaluations_response(self, response):
        self.evaluations_response = response

    def set_peers_assignment_response(self, response):
        self.peers_assignment = response

class MockGoogleStorage(GoogleStorage):

    def __init__(self):
        self.evaluations_raise_exception_by_reviewee = []

    def get_employees(self):
        return {
            'em_email': employees_collection().get('em_email'),
            'manager_em': employees_collection().get('manager_em'),
        }

    def get_forms(self):
        return {'SELF': 'first form'}

    def generate_eval_reports(self,
                              reviewee,
                              reviewee_evaluations,
                              employee_managers):
        if reviewee in self.evaluations_raise_exception_by_reviewee:
            raise Exception

        return []

    def get_peers_assignment(self):
        return {}

    def get_evaluations_will_raise_exception_for_reviewee(self, reviewee):
        self.evaluations_raise_exception_by_reviewee.append(reviewee)

    def write_peers_assignment(self, peers_assignment):
        return

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

    def send_communication(self, reviewer: Reviewer, kind: CommunicationKind):
        if reviewer.uid in self.raise_exception_for_reviewers:
            raise Exception("MockGmailChannel was asked to throw this exception")
        return

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

class GetReviewersUseCaseMock(
        GetReviewersUseCase,
        MockStorageFactory,
        MockEmployeeAdapter):

    def __init__(self):
        self.response = {}

    def set_get_reviewers(self, response):
        self.response = response

    def get_reviewers(self):
        return self.response

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
        self.employees_response = {}
        self.surveys_response = {}
        self.reviewers_response = {}
        self.status_response = {}
        self.communications_response = {}
        self.evalreports_response = {}

    def set_employees_response(self, response):
        self.employees_response = response

    def employees(self):
        self.update_calls('employees')
        return True, self.employees_response

    def set_surveys_response(self, response):
        self.surveys_response = response

    def surveys(self):
        self.update_calls('surveys')
        return True, self.surveys_response

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

    def set_communications_response(self, response):
        self.communications_response = response

    def communications(self, json_reviewers, kind: str):
        self.update_calls('communications')
        return True, self.communications_response

    def set_evalreports_response(self, response):
        self.evalreports_response = response

    def evalreports(self, uids):
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

class MockEvalyticsClient(EvalyticsClient, MockEvalyticsRequests):

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

    def send_communication(self, kind, reviewers, whitelist=None, dry_run: bool = False):
        self.update_calls('send_communication')
        self.dry_run = dry_run

    def generate_reports(self, whitelist=None, dry_run: bool = False):
        self.update_calls('generate_reports')
        self.dry_run = dry_run

    def get_whitelist(self):
        return []

    def get_retry_list(self):
        return []

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

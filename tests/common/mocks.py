
from configparser import ConfigParser

from evalytics.config import Config
from evalytics.models import Reviewer, GoogleSetup, GoogleFile
from evalytics.communications_channels import GmailChannel
from evalytics.storages import GoogleStorage
from evalytics.google_api import GoogleAPI
from evalytics.core import DataRepository, CommunicationsProvider
from evalytics.adapters import EmployeeAdapter

from client import EvalyticsRequests
from client import EvalyticsClient
from client import FileManager

from tests.common.employees import employees_collection

class MockDataRepository(DataRepository):

    def setup_storage(self):
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

class MockCommunicationsProvider(CommunicationsProvider):

    def __init__(self):
        self.raise_exception_for_reviewers = []

    def add_raise_exception_for_reviewer(self, reviewer_uid: str):
        self.raise_exception_for_reviewers.append(reviewer_uid)

    def send_communication(self, reviewer: Reviewer, data):
        if reviewer.uid in self.raise_exception_for_reviewers:
            raise Exception("MockCommunicationsProvider was asked to throw this exception")
        return

class MockEmployeeAdapter(EmployeeAdapter):

    def build_reviewers(self, employees, forms):
        return employees

    def build_eval_message(self, reviewer: Reviewer):
        return ""

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

class MockGoogleStorage(GoogleStorage):

    def setup(self):
        return

    def get_employee_map(self):
        return

    def get_forms_map(self):
        return

class MockGmailChannel(GmailChannel):

    def send(self, reviewer: Reviewer, data):
        return

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
    
    def read_company_domain(self):
        return "company.com"

    def read_company_number_of_employees(self):
        return 1000

    def set_needed_spreadhseets(self, needed_spreadhseets):
        self.needed_spreadsheets = needed_spreadhseets

class MockConfigParser(ConfigParser):

    def read(self, filename: str = ''):
        return {
            'GOOGLE': {
                'FOLDER': 'mock_folder',
                'ORGCHART': 'mock_orgchart',
                'FORM_MAP': 'mock_formmap',
            },
            'COMPANY': {
                'DOMAIN': 'mock_domain.com',
                'NUMBER_OF_EMPLOYEES': 20,
            }
        }

    def get(self, key, section):
        return self.read()[key][section]


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
        self.sendmail_response = {}

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

    def set_sendmail_response(self, response):
        self.sendmail_response = response

    def sendmail(self, json_reviewers):
        self.update_calls('sendmail')
        return True, self.sendmail_response

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
import pickle
import os.path
import json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from evalytics.mappers import GoogleFileDictToGoogleFile
from evalytics.models import EvalKind, GoogleApiClientHttpError
from evalytics.exceptions import GoogleApiClientHttpErrorException
from evalytics.exceptions import MissingGoogleDriveFolderException
from evalytics.exceptions import MissingGoogleDriveFileException

class GoogleAuth:
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = [
        # drive: Full, permissive scope to access all of a user's files,
        #        excluding the Application Data folder.
        'https://www.googleapis.com/auth/drive',
        # gmail: Send messages only. No read or modify privileges on mailbox.
        'https://www.googleapis.com/auth/gmail.send',
        # docs: Per-file access to files that the app created or opened.
        'https://www.googleapis.com/auth/drive.file',
        # sheets:
        # Allows read-only access to the user's sheets and their properties.
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        # appscripts:
        #'https://www.googleapis.com/auth/script.projects',
    ]

    @classmethod
    def authenticate(cls):
        """
        Obtaining auth with needed apis
        """
        creds = None
        # The file token.pickle stores the user's access
        # and refresh tokens, and is created automatically
        # when the authorization flow completes for the first time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', cls.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return creds

class GoogleService:

    __services_by_id = {}
    __credentials = None

    def get_service(self, service_id, service_version):
        if not service_id in self.__services_by_id:
            self.__services_by_id.update({
                service_id: {}
            })

        if not service_version in self.__services_by_id[service_id]:
            self.__services_by_id[service_id].update({
                service_version: build(
                    service_id,
                    service_version,
                    credentials=self.__get_credentials(),
                    cache_discovery=False)
            })

        return self.__services_by_id[service_id][service_version]

    def __get_credentials(self):
        if self.__credentials is None:
            self.__credentials = GoogleAuth.authenticate()
        return self.__credentials

class GoogleDrive(GoogleService):

    DRIVE_SERVICE_ID = 'drive'
    DRIVE_SERVICE_VERSION = 'v3'

    PERMISSION_ROLE_COMMENTER = 'commenter'

    MIMETYPE_FOLDER = 'application/vnd.google-apps.folder'
    MIMETYPE_DOCUMENT = 'application/vnd.google-apps.document'
    MIMETYPE_SPREADSHEET = 'application/vnd.google-apps.spreadsheet'

    QUERY_IS_FOLDER = f"mimeType='{MIMETYPE_FOLDER}'"
    QUERY_IS_SPREAD = f"mimeType='{MIMETYPE_FOLDER}'"
    QUERY_IS_SPREADSHEET = f"mimeType='{MIMETYPE_SPREADSHEET}'"

    def create_folder(self, name):
        file_metadata = {
            'name': name,
            'mimeType': GoogleDrive.MIMETYPE_FOLDER
        }
        drive_service = super().get_service(
            self.DRIVE_SERVICE_ID,
            self.DRIVE_SERVICE_VERSION
        )
        folder = drive_service.files().create(
            body=file_metadata,
            fields='id, name, parents').execute()

        return GoogleFileDictToGoogleFile().google_file_dict_to_google_file(folder)

    def update_file_parent(self, file_id, current_parent, new_parent):
        drive_service = super().get_service(
            self.DRIVE_SERVICE_ID,
            self.DRIVE_SERVICE_VERSION
        )
        file_update = drive_service.files().update(
            fileId=file_id,
            addParents=new_parent,
            removeParents=current_parent)
        file_update.execute()

    def list_files(self, page_token: str, query: str):
        drive_service = super().get_service(
            self.DRIVE_SERVICE_ID,
            self.DRIVE_SERVICE_VERSION
        )
        response = drive_service.files().list(
            q=query,
            pageSize=100,
            spaces='drive',
            corpora='user',
            fields='nextPageToken, files(id, name, parents)',
            pageToken=page_token).execute()

        google_files = [
            GoogleFileDictToGoogleFile().google_file_dict_to_google_file(google_file_dict)
            for google_file_dict in response.get('files', [])]
        next_page_token = response.get('nextPageToken', None)

        return google_files, next_page_token

    def copy_file(self, file_id, new_filename):
        drive_service = super().get_service(
            self.DRIVE_SERVICE_ID,
            self.DRIVE_SERVICE_VERSION
        )
        results = drive_service.files().copy(
            fileId=file_id,
            body={
                'name': new_filename,
                'mimeType': GoogleDrive.MIMETYPE_DOCUMENT
            }
        ).execute()
        return results.get('id')

    def create_permission(self, document_id: str, role: str, email_address):
        drive_service = super().get_service(
            self.DRIVE_SERVICE_ID,
            self.DRIVE_SERVICE_VERSION
        )
        drive_service.permissions().create(
            fileId=document_id,
            body={
                'type': 'user',
                'emailAddress': email_address,
                'role': role,
            }
        ).execute()

    #
    # High level API access
    #

    def get_folder(self, name):
        query = GoogleDrive.QUERY_IS_FOLDER
        return self.__get_file(query, name)

    def gdrive_list(self, path: str):
        path = list(filter(lambda x: x != '', path.split('/')))

        folder = self.get_folder(path[0])

        for path_element in path[1:]:
            query = f"{GoogleDrive.QUERY_IS_FOLDER} and '{folder.id}' in parents"
            folder = self.__get_file(query, path_element)

            if folder is None:
                raise MissingGoogleDriveFolderException(
                    "Missing folder: {}".format(path_element))

        query = f"{GoogleDrive.QUERY_IS_SPREADSHEET} and '{folder.id}' in parents"
        return self.__get_files(query)

    def gdrive_get_file(self, path: str):
        path = list(filter(lambda x: x != '', path.split('/')))

        folder = self.get_folder(path[0])
        path_elements = path[1 : len(path)-1]

        for path_element in path_elements:
            query = f"{GoogleDrive.QUERY_IS_FOLDER} and '{folder.id}' in parents"
            folder = self.__get_file(query, path_element)

            if folder is None:
                raise MissingGoogleDriveFolderException(
                    "Missing folder: {}".format(path_element))

        filename = path[len(path)-1]
        query = f"'{folder.id}' in parents"
        return self.__get_file(query, filename)

    def create_file(self):
        pass

    def __get_file(self, query: str, filename):
        try:
            page_token = None
            while True:
                google_files, next_page_token = self.list_files(
                    page_token=page_token,
                    query=query
                )
                for google_file in google_files:
                    if google_file.name == filename:
                        return google_file

                if next_page_token is None:
                    break
            return None
        except HttpError as e:
            error_reason = json.loads(e.content)
            error = error_reason['error']
            http_error = GoogleApiClientHttpError(
                error['code'],
                error['message'],
                error['status'],
                error['details'] if 'details' in error else []
            )
            raise GoogleApiClientHttpErrorException(http_error)

    def __get_files(self, query: str):
        try:
            page_token = None
            total_google_files = []
            while True:
                google_files, next_page_token = self.list_files(
                    page_token=page_token,
                    query=query
                )
                total_google_files = total_google_files + google_files

                if next_page_token is None:
                    return total_google_files
            return None
        except HttpError as e:
            error_reason = json.loads(e.content)
            error = error_reason['error']
            http_error = GoogleApiClientHttpError(
                error['code'],
                error['message'],
                error['status'],
                error['details'] if 'details' in error else []
            )
            raise GoogleApiClientHttpErrorException(http_error)

class SheetsService(GoogleService):

    SHEETS_SERVICE_ID = 'sheets'
    SHEETS_SERVICE_VERSION = 'v4'

    cached_file_values = {}

    def create_spreadsheet(self, filename):
        file_metadata = {
            'properties': {
                'title': filename,
            }
        }
        sheets_service = super().get_service(
            self.SHEETS_SERVICE_ID,
            self.SHEETS_SERVICE_VERSION
        )
        spreadsheet = sheets_service.spreadsheets().create(
            body=file_metadata,
            fields='spreadsheetId').execute()
        return spreadsheet

    def get_file_values(self, spreadsheet_id, rows_range):
        sheets_service = super().get_service(
            self.SHEETS_SERVICE_ID,
            self.SHEETS_SERVICE_VERSION
        )

        if spreadsheet_id in self.cached_file_values:
            if rows_range in self.cached_file_values[spreadsheet_id]:
                return self.cached_file_values[spreadsheet_id][rows_range]

        sheet = sheets_service.spreadsheets()

        try:
            result = sheet.values().get(
                spreadsheetId=spreadsheet_id,
                range=rows_range
            ).execute()
            values = result.get('values', [])

            if len(values) > 0:
                self.cached_file_values.update({
                    spreadsheet_id: {
                        rows_range: values
                    }
                })
            return values
        except HttpError as e:
            error_reason = json.loads(e.content)
            error = error_reason['error']
            http_error = GoogleApiClientHttpError(
                error['code'],
                error['message'],
                error['status'],
                error['details'] if 'details' in error else []
            )
            raise GoogleApiClientHttpErrorException(http_error)

    def update_file_values(self, spreadsheet_id, rows_range, value_input_option, values):
        sheets_service = super().get_service(
            self.SHEETS_SERVICE_ID,
            self.SHEETS_SERVICE_VERSION
        )
        sheet = sheets_service.spreadsheets()

        value_range_body = {
            'values': values
        }
        result = sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range=rows_range,
            valueInputOption=value_input_option,
            body=value_range_body
        ).execute()
        return result.get('values', [])

    #
    # High level API access
    #

    def open_file(self):
        pass

class GmailService(GoogleService):

    GMAIL_SERVICE_ID = 'gmail'
    GMAIL_SERVICE_VERSION = 'v1'

    def send_email(self, user_id, body):
        gmail_service = super().get_service(
            self.GMAIL_SERVICE_ID,
            self.GMAIL_SERVICE_VERSION
        )
        return gmail_service.users().messages().send(
            userId=user_id,
            body=body).execute()

class DocsService(GoogleService):

    DOCS_SERVICE_ID = 'docs'
    DOCS_SERVICE_VERSION = 'v1'

    ELEMENTS = 'elements'
    START_INDEX = 'startIndex'
    END_INDEX = 'endIndex'

    PARAGRAPH = 'paragraph'
    HORIZONTAL_RULE = 'horizontalRule'

    TEXT_RUN = 'textRun'
    CONTENT = 'content'

    def get_document(self, document_id):
        docs_service = super().get_service(
            self.DOCS_SERVICE_ID,
            self.DOCS_SERVICE_VERSION
        )
        return docs_service.documents().get(documentId=document_id).execute()

    def batch_update(self, document_id, requests):
        docs_service = super().get_service(
            self.DOCS_SERVICE_ID,
            self.DOCS_SERVICE_VERSION
        )
        docs_service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}).execute()

    def get_eval_report_style_tokens(self):
        return {
            'eval_title': {
                'start': 'start-eval-title',
                'end': 'end-eval-title'
            },
            'reviewer': {
                'start': 'start-reviewer',
                'end': 'end-reviewer',
            },
            'question': {
                'start': 'start-question',
                'end': 'end-question',
            },
            'answer': {
                'start': 'start-answer',
                'end': 'end-answer',
            },
        }

    def get_delete_tokens_requests(self):
        delete_tokens_requests = []
        for _, tokens in self.get_eval_report_style_tokens().items():
            delete_tokens_requests.append({
                    'replaceAllText': {
                    'containsText': {
                        'text': '%{}%'.format(tokens['start']),
                        'matchCase':  'true'
                    },
                    'replaceText': '',
                }
            })
            delete_tokens_requests.append({
                    'replaceAllText': {
                    'containsText': {
                        'text': '%{}%'.format(tokens['end']),
                        'matchCase':  'true'
                    },
                    'replaceText': '',
                }
            })
        return delete_tokens_requests

    def get_eval_report_style(self, kind, start_index, end_index):
        if kind == 'question':
            return {
                'updateTextStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'textStyle': {
                        'fontSize': {
                            'magnitude': 14,
                            'unit': 'PT'
                        },
                        'bold': False,
                    },
                    'fields': '*'
                }
            }
        elif kind == 'reviewer':
            return {
                'updateTextStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'textStyle': {
                        'fontSize': {
                            'magnitude': 16,
                            'unit': 'PT'
                        },
                        'bold': False,
                    },
                    'fields': '*'
                }
            }
        elif kind == 'eval_title':
            return {
                'updateTextStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'textStyle': {
                        'fontSize': {
                            'magnitude': 20,
                            'unit': 'PT'
                        },
                        'bold': True,
                    },
                    'fields': '*'
                }
            }
        elif kind == 'answer':
            return None
        else:
            raise NotImplementedError("eval report style not implemented")

class FilesAPI(GoogleDrive, SheetsService, DocsService):

    def create_sheet(self, folder_parent, folder, filename: str):
        spreadsheet = super().create_spreadsheet(filename)
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        super().update_file_parent(
            file_id=spreadsheet_id,
            current_parent=folder_parent,
            new_parent=folder.id
        )
        # TODO:
        # return create('/folder_parent/folder/filename', mimetype='blablabal.spreadsheet')
        return spreadsheet_id

    def get_file_rows_from_folder(self,
                                  foldername: str,
                                  filename: str,
                                  rows_range: str):
        file_path = f'/{foldername}/{filename}'
        google_file = super().gdrive_get_file(file_path)

        if google_file is None:
            raise MissingGoogleDriveFileException('Missing file: {}'.format(filename))

        values = super().get_file_values(
            google_file.id,
            rows_range)

        return values

    def insert_eval_report_in_document(self,
                                       eval_process_id,
                                       document_id,
                                       reviewee,
                                       reviewee_evaluations):
        eval_report_with_tokens = self.__build_eval_report_with_tokens(
            eval_process_id,
            reviewee_evaluations)
        self.__insert_eval_report_with_tokens(
            document_id,
            eval_report_with_tokens,
            reviewee)
        self.__apply_eval_report_style(document_id)
        self.__delete_tokens_from_document(document_id)

    def empty_document(self, document_id):
        document = super().get_document(document_id)
        content = document.get('body').get('content')
        insert_index = self.__get_indext_after_firt_horizontal_rule(content)
        end_index = self.__get_last_end_index(content)

        # Empty file
        if end_index in range(0, 2) or \
            insert_index >= end_index:
            return

        requests = [
            {
                'deleteContentRange':{
                    'range': {
                        'segmentId': '',
                        'startIndex': insert_index,
                        'endIndex': end_index
                    }
                }
            }
        ]
        super().batch_update(document_id=document_id, requests=requests)

    def ___build_styled_eval_report_element(self, element, content):
        style_tokens = super().get_eval_report_style_tokens()
        element_style = style_tokens.get(element, {'start':'', 'end':''})
        return '%{}%{}%{}%'.format(element_style['start'], content, element_style['end'])

    def __build_eval_report_with_tokens(self, eval_process_id, reviewee_evaluations):
        styled_title = self.___build_styled_eval_report_element('eval_title', eval_process_id)
        styled_eval_report = ''

        for reviewer_response in reviewee_evaluations:
            eval_kind = self.__get_human_readable_eval_kind(reviewer_response.eval_kind)
            styled_reviewer = self.___build_styled_eval_report_element(
                'reviewer',
                'Reviewer: %s, kind: %s' % (reviewer_response.reviewer, eval_kind))

            styled_responses = ''
            for question, answer in reviewer_response.eval_response:
                styled_question = self.___build_styled_eval_report_element('question', question)
                styled_answer = self.___build_styled_eval_report_element('answer', answer)
                styled_responses = '{}\n{}\n{}\n'.format(styled_responses, styled_question, styled_answer)

            styled_eval_report = '{}\n\n{}\n{}'.format(styled_eval_report, styled_reviewer, styled_responses)

        return '{}\n{}'.format(styled_title, styled_eval_report)

    def __get_human_readable_eval_kind(self, eval_kind):
        if eval_kind == EvalKind.SELF:
            return 'Self evaluation'
        elif eval_kind == EvalKind.PEER_MANAGER:
            return 'Report by direct report'
        elif eval_kind == EvalKind.MANAGER_PEER:
            return 'Report by direct manager'
        elif eval_kind == EvalKind.PEER_TO_PEER:
            return 'Report by peer'
        else:
            return ''

    def __insert_eval_report_with_tokens(self, document_id, eval_report_with_tokens, reviewee):
        document = super().get_document(document_id)
        content = document.get('body').get('content')
        insert_index = self.__get_indext_after_firt_horizontal_rule(content)

        requests = [
            {
                'insertText': {
                    "text": '\n{{EVAL}}\n',
                    "location": {
                        # object (Location)
                        "index": insert_index,
                    }
                }
            },
            {
                'replaceAllText': {
                    'containsText': {
                        'text': '{{EVAL}}',
                        'matchCase':  'true'
                    },
                    'replaceText': eval_report_with_tokens,
                }
            },
            {
                'replaceAllText': {
                    'containsText': {
                        'text': '{{employee-name}}',
                        'matchCase':  'true'
                    },
                    'replaceText': reviewee,
                },
            }
        ]
        super().batch_update(document_id=document_id, requests=requests)

    def __apply_eval_report_style(self, document_id):
        document = super().get_document(document_id)
        content = document.get('body').get('content')

        style_requests = []
        for item in content:
            if DocsService.PARAGRAPH in item:
                for element in item.get(DocsService.PARAGRAPH).get(DocsService.ELEMENTS):
                    if DocsService.TEXT_RUN in element and DocsService.CONTENT in element.get(DocsService.TEXT_RUN):
                        content = element.get(DocsService.TEXT_RUN).get(DocsService.CONTENT)
                        possible_tokens = content.split('%')

                        for token_uid, tokens in super().get_eval_report_style_tokens().items():
                            if tokens['start'] in possible_tokens and tokens['end']:
                                start_index = element.get(DocsService.START_INDEX)
                                end_index = element.get(DocsService.END_INDEX)
                                style_request = super().get_eval_report_style(token_uid, start_index, end_index)
                                if style_request is not None:
                                    style_requests.append(style_request)

        super().batch_update(document_id=document_id, requests=style_requests)

    def __delete_tokens_from_document(self, document_id):
        delete_token_requests = super().get_delete_tokens_requests()
        super().batch_update(
            document_id=document_id,
            requests=delete_token_requests)

    def __get_indext_after_firt_horizontal_rule(self, content):
        horizontal_rule_was_seen = False
        for item in content:
            if DocsService.PARAGRAPH in item:
                for element in item.get(DocsService.PARAGRAPH).get(DocsService.ELEMENTS):
                    if DocsService.HORIZONTAL_RULE in element:
                        horizontal_rule_was_seen = True
                        next_index_hr = element.get(DocsService.END_INDEX) + 1

                if horizontal_rule_was_seen:
                    break
        return next_index_hr

    def __get_last_end_index(self, content):
        last_item = content[len(content)-1]
        end_index = 0

        for element in last_item.get(DocsService.PARAGRAPH).get(DocsService.ELEMENTS):
            end_index = element.get(DocsService.START_INDEX)

            if DocsService.TEXT_RUN in element:
                text_run = element.get(DocsService.TEXT_RUN)
                if DocsService.CONTENT in text_run:
                    if text_run.get(DocsService.CONTENT) == '\n':
                        return end_index

        return end_index

class GmailAPI(GmailService):

    AUTHENTICATED_USER = 'me'

    def send_message(self, user_id, message):
        """Send an email message.

        Args:
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

        Returns:
        Sent Message.
        """
        message = super().send_email(
            user_id=user_id,
            body=message
        )
        return message

class GoogleAPI(FilesAPI, GmailAPI):
    'Composition of google APIs'

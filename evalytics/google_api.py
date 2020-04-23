import pickle
import os.path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

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
        if service_id not in self.__services_by_id:
            self.__services_by_id[service_id] = build(
                service_id,
                service_version,
                credentials=self.__get_credentials(),
                cache_discovery=False)
        return self.__services_by_id[service_id]

    def __get_credentials(self):
        if self.__credentials is None:
            self.__credentials = GoogleAuth.authenticate()
        return self.__credentials


class DriveService(GoogleService):

    DRIVE_SERVICE_ID = 'drive'
    DRIVE_SERVICE_VERSION = 'v3'

    PERMISSION_ROLE_COMMENTER = 'commenter'

    def create_drive_folder(self, file_metadata):
        drive_service = super().get_service(
            self.DRIVE_SERVICE_ID,
            self.DRIVE_SERVICE_VERSION
        )
        return drive_service.files().create(
            body=file_metadata,
            fields='id, parents').execute()

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
        return drive_service.files().list(
            q=query,
            pageSize=100,
            spaces='drive',
            corpora='user',
            fields='nextPageToken, files(id, name, parents)',
            pageToken=page_token).execute()

    def copy_file(self, file_id, new_filename):
        drive_service = super().get_service(
            self.DRIVE_SERVICE_ID,
            self.DRIVE_SERVICE_VERSION
        )
        results = drive_service.files().copy(
            fileId=file_id,
            body={
                'name': new_filename,
                'mimeType': 'application/vnd.google-apps.document'
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

class SheetsService(GoogleService):

    SHEETS_SERVICE_ID = 'sheets'
    SHEETS_SERVICE_VERISON = 'v4'

    def create_spreadsheet(self, file_metadata):
        sheets_service = super().get_service(
            self.SHEETS_SERVICE_ID,
            self.SHEETS_SERVICE_VERISON
        )
        spreadsheet = sheets_service.spreadsheets().create(
            body=file_metadata,
            fields='spreadsheetId').execute()
        return spreadsheet

    def get_file_values(self, spreadsheet_id, rows_range):
        sheets_service = super().get_service(
            self.SHEETS_SERVICE_ID,
            self.SHEETS_SERVICE_VERISON
        )
        sheet = sheets_service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=rows_range
        ).execute()
        return result.get('values', [])

class GmailService(GoogleService):

    GMAIL_SERVICE_ID = 'gmail'
    GMAIL_SERVICE_VERSION = 'v1'

    def send(self, user_id, body):
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

class FilesAPI(DriveService, SheetsService, DocsService):

    def create_folder(self, name: str):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = super().create_drive_folder(file_metadata)
        return folder

    def create_sheet(self, folder_parent, folder, filename: str):
        file_metadata = {
            'properties': {
                'title': filename,
            }
        }
        spreadsheet = super().create_spreadsheet(file_metadata)
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        super().update_file_parent(
            file_id=spreadsheet_id,
            current_parent=folder_parent,
            new_parent=folder.get('id')
        )
        return spreadsheet_id

    def get_folder(self, name):
        query = "mimeType='application/vnd.google-apps.folder'"
        return self.__get_file(query, name)

    def get_file_id_from_folder(self, folder_id, filename):
        query = "'%s' in parents" % folder_id
        file = self.__get_file(query, filename)

        if file is not None:
            return file.get('id')

        return None

    def get_folder_from_folder(self, foldername, parent_foldername):
        folder = self.get_folder(parent_foldername)
        if folder is not None:
            is_folder = "mimeType='application/vnd.google-apps.folder'"
            query = "%s and '%s' in parents" % (is_folder, folder.get('id'))
            folder = self.__get_file(query, foldername)
        return folder

    def get_files_from_folder(self, folder_id):
        is_spreadsheet = "mimeType='application/vnd.google-apps.spreadsheet'"
        query = "%s and '%s' in parents" % (is_spreadsheet, folder_id)
        files = self.__get_files(query)
        return files

    def get_file_rows_from_folder(self,
                                  foldername: str,
                                  filename: str,
                                  rows_range: str):
        folder = self.get_folder(name=foldername)
        spreadsheet_id = self.get_file_id_from_folder(
            folder_id=folder.get('id'),
            filename=filename)

        values = super().get_file_values(
            spreadsheet_id,
            rows_range)

        return values

    def insert_eval_report_in_document(self, eval_process_id, document_id, reviewee_evaluations):
        # TODO: insertar tokens en preguntas/respuestas
        eval_report_with_tokens = self.__build_eval_report_with_tokens(
            eval_process_id,
            reviewee_evaluations)
        self.__insert_eval_report_with_tokens(
            document_id,
            eval_report_with_tokens)
        self.__apply_eval_report_style(document_id)
        self.__delete_tokens_from_document(document_id)

    def add_comenter_permission(self, document_id, emails):
        for email in emails:
            super().create_permission(
                document_id=document_id,
                role=DriveService.PERMISSION_ROLE_COMMENTER,
                email_address=email
            )

    def ___build_styled_eval_report_element(self, element, content):
        style_tokens = super().get_eval_report_style_tokens()
        element_style = style_tokens.get(element, {'start':'', 'end':''})
        return '%{}%{}%{}%'.format(element_style['start'], content, element_style['end'])

    def __build_eval_report_with_tokens(self, eval_process_id, reviewee_evaluations):
        styled_title = self.___build_styled_eval_report_element('eval_title', eval_process_id)
        styled_eval_report = ''

        for reviewer_response in reviewee_evaluations:
            styled_reviewer = self.___build_styled_eval_report_element(
                'reviewer', 
                'Reviewer: %s, kind: %s' % (reviewer_response.reviewer, reviewer_response.eval_kind.name.lower()))

            styled_responses = ''
            for question, answer in reviewer_response.eval_response:
                styled_question = self.___build_styled_eval_report_element('question', question)
                styled_answer = self.___build_styled_eval_report_element('answer', answer)
                styled_responses = '{}\n{}\n{}\n'.format(styled_responses, styled_question, styled_answer)

            styled_eval_report = '{}\n\n{}\n{}'.format(styled_eval_report, styled_reviewer, styled_responses)

        return '{}\n{}'.format(styled_title, styled_eval_report)

    def __insert_eval_report_with_tokens(self, document_id, eval_report_with_tokens):
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
                    'replaceText': 'egarcia',
                },
            }
        ]
        super().batch_update(document_id=document_id, requests=requests)

    def __apply_eval_report_style(self, document_id):
        document = super().get_document(document_id)
        content = document.get('body').get('content')

        START_INDEX = 'startIndex'
        END_INDEX = 'endIndex'

        ELEMENTS = 'elements'
        TEXT_RUN = 'textRun'
        PARAGRAPH = 'paragraph'

        CONTENT = 'content'

        style_requests = []
        for item in content:
            if PARAGRAPH in item:
                for element in item.get(PARAGRAPH).get(ELEMENTS):
                    if TEXT_RUN in element and CONTENT in element.get(TEXT_RUN):
                        content = element.get(TEXT_RUN).get(CONTENT)
                        possible_tokens = content.split('%')

                        for token_uid, tokens in super().get_eval_report_style_tokens().items():
                            if tokens['start'] in possible_tokens and tokens['end']:
                                start_index = element.get(START_INDEX)
                                end_index = element.get(END_INDEX)
                                style_request = super().get_eval_report_style(token_uid, start_index, end_index)
                                if style_request is not None:
                                    style_requests.append(style_request)

        super().batch_update(document_id=document_id, requests=style_requests)

    def __delete_tokens_from_document(self, document_id):
        delete_token_requests = super().get_delete_tokens_requests()
        super().batch_update(document_id=document_id, requests=delete_token_requests)

    def get_file_rows(self, file_id: str, rows_range: str):
        return super().get_file_values(
            file_id,
            rows_range
        )

    def __get_file(self, query: str, filename):
        try:
            page_token = None
            while True:
                response = super().list_files(
                    page_token=page_token,
                    query=query
                )
                for file in response.get('files', []):
                    if file.get('name') == filename:
                        return file

                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
            return None
        except HttpError as err:
            # TODO: manage this
            print(err)
            raise err

    def __get_files(self, query: str):
        try:
            page_token = None
            files = []
            while True:
                response = super().list_files(
                    page_token=page_token,
                    query=query
                )
                for file in response.get('files', []):
                    files.append(file)

                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    return files
            return None
        except HttpError as err:
            # TODO: manage this
            print(err)
            raise err

    def __get_indext_after_firt_horizontal_rule(self, content):
        ELEMENTS = 'elements'
        END_INDEX = 'endIndex'
        PARAGRAPH = 'paragraph'
        HORIZONTAL_RULE = 'horizontalRule'

        horizontal_rule_was_seen = False
        for item in content:
            if PARAGRAPH in item:
                for element in item.get(PARAGRAPH).get(ELEMENTS):
                    if HORIZONTAL_RULE in element:
                        horizontal_rule_was_seen = True
                        next_index_hr = element.get(END_INDEX) + 1

                if horizontal_rule_was_seen:
                    break
        return next_index_hr

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
        message = super().send(
            user_id=user_id,
            body=message
        )
        return message

class GoogleAPI(FilesAPI, GmailAPI):
    'Composition of google APIs'

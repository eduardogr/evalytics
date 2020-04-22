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

class DriveService:

    DRIVE_SERVICE_ID = 'drive'
    DRIVE_SERVICE_VERSION = 'v3'

    __credentials = None
    __drive_service = None

    def create_drive_folder(self, file_metadata):
        return self.__get_drive_service().files().create(
            body=file_metadata,
            fields='id, parents').execute()

    def update_file_parent(self, file_id, current_parent, new_parent):
        file_update = self.__get_drive_service().files().update(
            fileId=file_id,
            addParents=new_parent,
            removeParents=current_parent)
        file_update.execute()

    def list_files(self, page_token: str, query: str):
        drive_service = self.__get_drive_service()
        return drive_service.files().list(
            q=query,
            pageSize=100,
            spaces='drive',
            corpora='user',
            fields='nextPageToken, files(id, name, parents)',
            pageToken=page_token).execute()

    def __get_drive_service(self):
        if self.__drive_service is None:
            self.__drive_service = build(
                self.DRIVE_SERVICE_ID,
                self.DRIVE_SERVICE_VERSION,
                credentials=self.__get_credentials(),
                cache_discovery=False)
        return self.__drive_service

    def __get_credentials(self):
        if self.__credentials is None:
            self.__credentials = GoogleAuth.authenticate()
        return self.__credentials

class SheetsService:

    SHEETS_SERVICE_ID = 'sheets'
    SHEETS_SERVICE_VERISON = 'v4'

    __credentials = None
    __sheets_service = None

    def create_spreadsheet(self, file_metadata):
        spreadsheet = self.__get_sheets_service().spreadsheets().create(
            body=file_metadata,
            fields='spreadsheetId').execute()
        return spreadsheet

    def get_file_values(self, spreadsheet_id, rows_range):
        sheet = self.__get_sheets_service().spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=rows_range
        ).execute()
        return result.get('values', [])

    def __get_sheets_service(self):
        if self.__sheets_service is None:
            self.__sheets_service = build(
                self.SHEETS_SERVICE_ID,
                self.SHEETS_SERVICE_VERISON,
                credentials=self.__get_credentials(),
                cache_discovery=False)
        return self.__sheets_service

    def __get_credentials(self):
        if self.__credentials is None:
            self.__credentials = GoogleAuth.authenticate()
        return self.__credentials

class GmailService:

    GMAIL_SERVICE_ID = 'gmail'
    GMAIL_SERVICE_VERSION = 'v1'

    __credentials = None
    __gmail_service = None

    def send(self, user_id, body):
        return self.__get_gmail_service().users().messages().send(
            userId=user_id,
            body=body).execute()

    def __get_gmail_service(self):
        if self.__gmail_service is None:
            self.__gmail_service = build(
                self.GMAIL_SERVICE_ID,
                self.GMAIL_SERVICE_VERSION,
                credentials=self.__get_credentials(),
                cache_discovery=False)
        return self.__gmail_service

    def __get_credentials(self):
        if self.__credentials is None:
            self.__credentials = GoogleAuth.authenticate()
        return self.__credentials

class FilesAPI(DriveService, SheetsService):

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

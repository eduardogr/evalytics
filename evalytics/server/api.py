from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .auth import GoogleAuth


class FilesAPI:

    DRIVE_SERVICE_ID = 'drive'
    DRIVE_SERVICE_VERSION = 'v3'
    SHEETS_SERVICE_ID = 'sheets'
    SHEETS_SERVICE_VERISON = 'v4'

    __credentials = None
    __drive_service = None
    __sheets_service = None

    def create_folder(self, name: str):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self.__get_drive_service().files().create(
            body=file_metadata,
            fields='id, parents').execute()
        return folder

    def create_spreadhsheet(self, folder, folder_parent):
        spreadsheet = {
            'properties': {
                'title': 'orgchart',
            }
        }
        spreadsheet = self.__get_sheets_service().spreadsheets().create(
            body=spreadsheet,
            fields='spreadsheetId').execute()
        file_update = self.__get_drive_service().files().update(
            fileId=spreadsheet.get('spreadsheetId'),
            addParents=folder.get('id'),
            removeParents=folder_parent)
        file_update.execute()
        return spreadsheet.get('spreadsheetId')

    def get_folder(self, name):
        # TODO: differentiate between file and folder,
        # to not return a file with the same name
        try:
            drive_service = self.__get_drive_service()

            page_token = None
            while True:
                response = drive_service.files().list(
                    pageSize=20,
                    spaces='drive',
                    fields='nextPageToken, files(id, name, parents)',
                    pageToken=page_token).execute()

                for file in response.get('files', []):
                    if file.get('name') == name:
                        return file
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break

            return None
        except HttpError as err:
            # TODO: manage this
            print(err)
            raise err

    def get_file_id_from_folder(self, folder_id, filename):
        try:
            drive_service = self.__get_drive_service()

            page_token = None
            while True:
                response = drive_service.files().list(
                    q="'%s' in parents" % folder_id,
                    spaces='drive',
                    fields='nextPageToken, files(id, name)',
                    pageToken=page_token).execute()

                for file in response.get('files', []):
                    if file.get('name') == filename:
                        return file.get('id')

                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
            return None
        except HttpError as err:
            # TODO: manage this
            print(err)
            raise err

    def get_file_rows(self, foldername: str, filename: str, rows_range: str):
        sheet = self.__get_sheets_service().spreadsheets()

        folder = self.get_folder(name=foldername)
        spreadsheet_id = self.get_file_id_from_folder(
            folder_id=folder.get('id'),
            filename=filename)

        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=rows_range
        ).execute()

        return result.get('values', [])

    def __get_drive_service(self):
        if self.__drive_service is None:
            self.__drive_service = build(
                self.DRIVE_SERVICE_ID,
                self.DRIVE_SERVICE_VERSION,
                credentials=self.__get_credentials(),
                cache_discovery=False)
        return self.__drive_service

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

class GmailAPI:

    GMAIL_SERVICE_ID = 'gmail'
    GMAIL_SERVICE_VERSION = 'v1'
    AUTHENTICATED_USER = 'me'

    __credentials = None
    __gmail_service = None

    def send_message(self, user_id, message):
        """Send an email message.

        Args:
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

        Returns:
        Sent Message.
        """
        message = self.__get_gmail_service().users().messages().send(
            userId=user_id, body=message).execute()
        return message

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

class GoogleAPI(FilesAPI, GmailAPI):
    'Composition of google APIs'

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .auth import GoogleAuth
from .models import Employee, Team


class Storage:

    @classmethod
    def get_employee_list(cls):
        raise NotImplementedError


class InMemoryStorage(Storage):

    @classmethod
    def get_employee_list(cls):
        raise NotImplementedError


class GoogleStorage(Storage):

    ORG_CHART_NAME = 'orgchart'

    __credentials = None

    @classmethod
    def get_employee_list(cls):
        creds = cls.__get_google_credentials()
        sheets_service = build('sheets', 'v4', credentials=creds)
        sheet = sheets_service.spreadsheets()

        folder = cls.__get_folder(name='evalytics')
        spreadsheet_id = cls.__get_file_id_from_folder(
            folder_id=folder.get('id'),
            filename=cls.ORG_CHART_NAME)

        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range='A1:F10'
        ).execute()
        values = result.get('values', [])

        employees = []
        if values:
            for row in values:
                team = Team(
                    name=row[3],
                    manager=row[5],
                    manager_one_level_up=row[6])
                employee = Employee(
                    name=row[0],
                    mail=row[1],
                    position=row[4],
                    team=team)
                employees.append(employee)
                print('%s, %s' % (row[0], row[1]))

        return employees

    @classmethod
    def __get_folder(cls, name):
        # TODO: differentiate between file and folder, 
        # to not return a file with the same name
        creds = cls.__get_google_credentials()
        drive_service = build('drive', 'v3', credentials=creds)

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

    @classmethod
    def __get_file_id_from_folder(cls, folder_id, filename):
        creds = cls.__get_google_credentials()
        drive_service = build('drive', 'v3', credentials=creds)

        try:
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

    @classmethod
    def __get_google_credentials(cls):
        if cls.__credentials is None:
            cls.__credentials = GoogleAuth.authenticate()
        return cls.__credentials


class GoogleDriveClient:
    pass

class GoogleSheetsClient:
    pass

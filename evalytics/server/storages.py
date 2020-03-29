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

    STORAGE_FOLDER_NAME = 'evalytics'
    ORG_CHART_NAME = 'orgchart'
    ORG_CHART_RANGE = 'A1:F10'

    DRIVE_SERVICE_ID = 'drive'
    DRIVE_SERVICE_VERSION = 'v3'
    SHEETS_SERVICE_ID = 'sheets'
    SHEETS_SERVICE_VERISON = 'v4'

    __credentials = None
    __drive_service = None
    __sheets_service = None

    @classmethod
    def get_employee_list(cls):
        sheet = cls.__get_sheets_service().spreadsheets()

        folder = cls.__get_folder(name=cls.STORAGE_FOLDER_NAME)
        spreadsheet_id = cls.__get_file_id_from_folder(
            folder_id=folder.get('id'),
            filename=cls.ORG_CHART_NAME)

        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=cls.ORG_CHART_RANGE
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

        return employees

    @classmethod
    def __get_folder(cls, name):
        # TODO: differentiate between file and folder,
        # to not return a file with the same name
        try:
            drive_service = cls.__get_drive_service()

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

    @classmethod
    def __get_file_id_from_folder(cls, folder_id, filename):
        try:
            drive_service = cls.__get_drive_service()

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
    def __get_sheets_service(cls):
        if cls.__sheets_service is None:
            cls.__sheets_service = build(
                cls.SHEETS_SERVICE_ID, 
                cls.SHEETS_SERVICE_VERISON, 
                credentials=cls.__get_credentials())
        return cls.__sheets_service

    @classmethod
    def __get_drive_service(cls):
        if cls.__drive_service is None:
            cls.__drive_service = build(
                cls.DRIVE_SERVICE_ID,
                cls.DRIVE_SERVICE_VERSION,
                credentials=cls.__get_credentials())
        return cls.__drive_service

    @classmethod
    def __get_credentials(cls):
        if cls.__credentials is None:
            cls.__credentials = GoogleAuth.authenticate()
        return cls.__credentials

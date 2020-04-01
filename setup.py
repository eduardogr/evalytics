from __future__ import print_function
from googleapiclient.discovery import build
from evalytics.server.auth import GoogleAuth
from evalytics.server.storages import GoogleStorage

def main():
    folder_name = 'evalytics'
    orgchart_filename = 'orgchart'

    creds = GoogleAuth.authenticate()
    drive_service = build('drive', 'v3', credentials=creds)
    sheet_service = build('sheets', 'v4', credentials=creds)

    # Folder setup
    folder = GoogleStorage.__get_folder(name=folder_name)
    if folder is None:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive_service.files().create(
            body=file_metadata,
            fields='id, parents').execute()

    print('Folder ID: %s' % folder.get('id'))
    folder_parent = folder.get('parents')[0]

    # Sheet setup
    spreadheet_id = GoogleStorage__.get_file_id_from_folder(
        folder_id=folder.get('id'),
        filename=orgchart_filename)

    if spreadheet_id is None:
        spreadsheet = {
            'properties': {
                'title': 'orgchart',
            }
        }
        spreadsheet = sheet_service.spreadsheets().create(
            body=spreadsheet,
            fields='spreadsheetId').execute()
        file_update = drive_service.files().update(
            fileId=spreadsheet.get('spreadsheetId'),
            addParents=folder.get('id'),
            removeParents=folder_parent)
        file_update.execute()
        spreadheet_id = spreadsheet.get('spreadsheetId')

    print('Spreadsheet ID: {0}'.format(spreadheet_id))

if __name__ == '__main__':
    main()

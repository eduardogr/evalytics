#!/usr/bin/python3

from __future__ import print_function
from googleapiclient.discovery import build

from auth import GoogleAuth

def main():
    creds = GoogleAuth.authenticate()

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=50,
        fields="nextPageToken, files(id, name)"
    ).execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

if __name__ == '__main__':
    main()

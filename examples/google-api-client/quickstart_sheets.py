from __future__ import print_function
from googleapiclient.discovery import build

from auth import GoogleAuth

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'

def main():
    creds = GoogleAuth.authenticate()
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.get(spreadsheetId=SAMPLE_SPREADSHEET_ID).execute()

    for k, v in result.items():
        print(k)
        print(v)
        print()

if __name__ == '__main__':
    main()

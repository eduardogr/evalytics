from __future__ import print_function

from googleapiclient import errors
from googleapiclient.discovery import build

from auth import GoogleAuth

SAMPLE_CODE = '''
function helloWorld() {
  console.log("Hello, Evalytics!");
}
'''.strip()

SAMPLE_MANIFEST = '''
{
  "timeZone": "America/New_York",
  "exceptionLogging": "CLOUD"
}
'''.strip()

def main():
    creds = GoogleAuth.authenticate()

    service = build('script', 'v1', credentials=creds)

    # Call the Apps Script API
    try:
        # Create a new project
        request = {'title': 'My evalytics quickstart Script'}
        response = service.projects().create(body=request).execute()

        # Upload two files to the project
        request = {
            'files': [{
                'name': 'hello',
                'type': 'SERVER_JS',
                'source': SAMPLE_CODE
            }, {
                'name': 'appsscript',
                'type': 'JSON',
                'source': SAMPLE_MANIFEST
            }]
        }
        response = service.projects().updateContent(
            body=request,
            scriptId=response['scriptId']).execute()
        print('https://script.google.com/d/' + response['scriptId'] + '/edit')
    except errors.HttpError as error:
        # The API encountered a problem.
        print(error.content)


if __name__ == '__main__':
    main()
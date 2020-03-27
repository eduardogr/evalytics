import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GoogleAuth:
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = [
        # drive: Per-file access to files created or opened by the app.
        'https://www.googleapis.com/auth/drive.file',
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

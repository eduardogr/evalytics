from googleapiclient.discovery import build

from .auth import GoogleAuth


class CommunicationsChannel:

    @classmethod
    def send(cls, destiny, data):
        raise NotImplementedError


class StdOutputChannel(CommunicationsChannel):

    @classmethod
    def send(cls, destiny, data):
        print('To: %s\nData: %s' %(destiny, data))


class GmailChannel(CommunicationsChannel):

    GMAIL_SERVICE_ID = 'gmail'
    GMAIL_SERVICE_VERSION = 'v1'

    __credentials = None
    __gmail_service = None


    @classmethod
    def send(cls, destiny, data):
        raise NotImplementedError

    @classmethod
    def __get_gmail_service(cls):
        cls.__gmail_service = build(
            cls.GMAIL_SERVICE_ID,
            cls.GMAIL_SERVICE_VERSION,
            credentials=cls.__get_credentials())

    @classmethod
    def __get_credentials(cls):
        if cls.__credentials is None:
            cls.__credentials = GoogleAuth.authenticate()
        return cls.__credentials

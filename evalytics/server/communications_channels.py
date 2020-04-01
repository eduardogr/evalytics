import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        cls.__send_message(
            user_id='me',
            message=cls.__create_message(
                sender='me',
                to=destiny,
                subject='Eval 180 Test',
                message_text=data
            )
        )

    @classmethod
    def __create_message(cls, sender, to, subject, message_text):
        """Create a message for an email.

        Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

        Returns:
        An object containing a base64url encoded email object.
        """
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        message.attach(MIMEText(message_text, 'plain'))
        return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    @classmethod
    def __send_message(cls, user_id, message):
        """Send an email message.

        Args:
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

        Returns:
        Sent Message.
        """
        message = cls.__get_gmail_service().users().messages().send(
            userId=user_id, body=message).execute()
        return message

    @classmethod
    def __get_gmail_service(cls):
        if cls.__gmail_service is None:
            cls.__gmail_service = build(
                cls.GMAIL_SERVICE_ID,
                cls.GMAIL_SERVICE_VERSION,
                credentials=cls.__get_credentials(),
                cache_discovery=False)
        return cls.__gmail_service


    @classmethod
    def __get_credentials(cls):
        if cls.__credentials is None:
            cls.__credentials = GoogleAuth.authenticate()
        return cls.__credentials

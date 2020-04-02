import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from googleapiclient.discovery import build

from .auth import GoogleAuth
from .models import Employee


class CommunicationsChannel:

    @classmethod
    def send(cls, employee: Employee, data):
        raise NotImplementedError


class StdOutputChannel(CommunicationsChannel):

    @classmethod
    def send(cls, employee: Employee, data):
        print('To: %s\nData: %s' %(employee.uid, data))


class GmailChannel(CommunicationsChannel):

    GMAIL_SERVICE_ID = 'gmail'
    GMAIL_SERVICE_VERSION = 'v1'
    MY_GOOGLE_USER_ID = 'me'

    EVAL_SUBJECT = 'Evalytics: You can now complete your evaluation assignments!'

    __credentials = None
    __gmail_service = None

    @classmethod
    def send(cls, employee: Employee, data):
        destiny = employee.mail
        cls.__send_message(
            user_id=cls.MY_GOOGLE_USER_ID,
            message=cls.__create_message(
                sender=cls.MY_GOOGLE_USER_ID,
                to=destiny,
                subject=cls.EVAL_SUBJECT,
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
        return {
            'raw': base64.urlsafe_b64encode(
                message.as_string().encode()).decode()
        }

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

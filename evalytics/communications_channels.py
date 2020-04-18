from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

from .google_api import GoogleAPI
from .config import Config
from .models import Reviewer

class GmailChannel(GoogleAPI, Config):

    def send(self, reviewer: Reviewer, data):
        destiny = reviewer.mail
        mail_subject = super().read_mail_subject()
        super().send_message(
            user_id=GoogleAPI.AUTHENTICATED_USER,
            message=self.__create_message(
                sender=GoogleAPI.AUTHENTICATED_USER,
                to=destiny,
                subject=mail_subject,
                message_text=data
            )
        )

    def __create_message(self, sender, to, subject, message_text):
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
        message.attach(MIMEText(message_text, 'html'))
        return {
            'raw': base64.urlsafe_b64encode(
                message.as_string().encode()).decode()
        }

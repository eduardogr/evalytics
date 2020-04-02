from __future__ import print_function
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build

from auth import GoogleAuth

def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEMultipart(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message.attach(MIMEText(message_text, 'plain'))
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


def send_message(service, user_id, message):
    """Send an email message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

    Returns:
    Sent Message.
    """
    message = (service.users().messages().send(
        userId=user_id, body=message).execute())
    print('Message Id: %s' % message['id'])
    return message


def main():
    creds = GoogleAuth.authenticate()

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    send_message(
        service=service,
        user_id='me',
        message=create_message(
            sender='me', 
            to='egarcia@tuenti.com', 
            subject='Quickstart Gmail',
            message_text='Testing gmail api'
        )
    )

if __name__ == '__main__':
    main()

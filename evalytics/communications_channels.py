from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from slack import WebClient
from slack.errors import SlackApiError

from evalytics.google_api import GoogleAPI
from evalytics.models import Reviewer, EvalKind
from evalytics.config import Config, ProvidersConfig

class CommunicationChannelFactory(Config):

    def get_communication_channel(self):
        communication_channel_provider = super().read_communication_channel_provider()
        if communication_channel_provider == ProvidersConfig.GMAIL:
            return GmailChannel()

        elif communication_channel_provider == ProvidersConfig.SLACK:
            return SlackChannel()

        raise ValueError(communication_channel_provider)

class SlackChannel(Config):

    def send_communication(self, reviewer: Reviewer, is_reminder: bool):
        if is_reminder:
            message = 'You have pending evals:'
        else:
            message = 'You have new assignments !'

        token = super().get_slack_token()
        text_param = super().get_slack_text_param()
        channel_param = super().get_slack_channel_param()
        as_user_param = super().slack_message_as_user_param()
        is_direct_message = super().slack_message_is_direct()

        if is_direct_message:
            channel = channel_param.format(reviewer.uid)

        client = WebClient(token=token)
        blocks = self.__build_blocks(text_param.format(message), reviewer)

        try:
            _ = client.chat_postMessage(
                channel=channel,
                blocks=blocks,
                as_user=as_user_param)

        except SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            #print(f"Got an error: {e.response['error']}")

    def __build_blocks(self, message, reviewer: Reviewer):
        list_of_evals = ''
        for e_eval in reviewer.evals:
            if e_eval.kind is EvalKind.SELF:
                reviewee = 'Your self review'
            else:
                reviewee = e_eval.reviewee

            list_of_evals = list_of_evals + \
                    '- <' + e_eval.form + '|*' + reviewee + '*>\n'

        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hi {}:\n{}".format(reviewer.uid, message)
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "{}".format(list_of_evals)
                }
            }
        ]

class GmailChannel(GoogleAPI, Config):

    def send_communication(self, reviewer: Reviewer, is_reminder: bool):
        if is_reminder:
            mail_subject = super().read_reminder_mail_subject()
            message = 'You have pending evals:'
        else:
            mail_subject = super().read_mail_subject()
            message = 'You have new assignments !'

        destiny = reviewer.mail
        message_text = self.__build_message_text(message, reviewer)
        super().send_message(
            user_id=GoogleAPI.AUTHENTICATED_USER,
            message=self.__create_message(
                sender=GoogleAPI.AUTHENTICATED_USER,
                receiver=destiny,
                subject=mail_subject,
                message_text=message_text
            )
        )

    def __create_message(self, sender, receiver, subject, message_text):
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
        message['to'] = receiver
        message['from'] = sender
        message['subject'] = subject
        message.attach(MIMEText(message_text, 'html'))
        return {
            'raw': base64.urlsafe_b64encode(
                message.as_string().encode()).decode()
        }

    def __build_message_text(self, message, reviewer: Reviewer):
        list_of_evals = ''
        for e_eval in reviewer.evals:
            if e_eval.kind is EvalKind.SELF:
                reviewee = 'Your self review'
            else:
                reviewee = e_eval.reviewee

            list_of_evals = list_of_evals + \
                    '<a href="' + e_eval.form \
                    + '" style="color:#0ADA7C;display:block;margin:5px 0" target="_blank"><b>'\
                    + reviewee + '</b></a>'

        return '''<div><table style="font-family:HelveticaNeue-Light,Helvetica Neue Light,Helvetica Neue,Helvetica,Arial,Lucida Grande,sans-serif;text-align:center;color:#F6F6F6;font-size:15px" width="100%" cellspacing="0" cellpadding="0" border="0" bgcolor="#EEEEEE">
	<tbody><tr height="60" bgcolor="#000000;"><td style="text-align:left"></td></tr><tr><td>
			<table style="max-width:615px;padding:30px 7% 30px;border-bottom:2px solid #EEEEEE;border-radius:5px;text-align:center" width="100%" cellspacing="0" cellpadding="0" border="0" bgcolor="#fff" align="center">
			<tbody><tr><td><h1 style="font-size:25px;font-weight:normal;letter-spacing:-1px;color:#757575;padding:0 0 10px">
            Hi {0},</h1>
            <b></b><p style="color:#757575;line-height:23px;padding:30px auto">
                {1}
            </b></p></td>
            </tr>
            <tr><td style="padding:10px 0">
                    {2}
            </td></tr></tbody></tr></table></div>'''.format(reviewer.uid, message, list_of_evals)

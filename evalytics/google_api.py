from googledrive.api import GoogleService
from googledrive.api import GoogleDrive, SheetsService
from googledrive.exceptions import MissingGoogleDriveFileException

from evalytics.models import EvalKind


# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    # drive: Full, permissive scope to access all of a user's files,
    #        excluding the Application Data folder.
    'https://www.googleapis.com/auth/drive',
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

CREDENTIALS = 'credentials.json'

class GmailService(GoogleService):

    GMAIL_SERVICE_ID = 'gmail'
    GMAIL_SERVICE_VERSION = 'v1'

    def __init__(self):
        GoogleService.__init__(self, CREDENTIALS, SCOPES)

    def send_email(self, user_id, body):
        gmail_service = super().get_service(
            self.GMAIL_SERVICE_ID,
            self.GMAIL_SERVICE_VERSION
        )
        return gmail_service.users().messages().send(
            userId=user_id,
            body=body).execute()

class DocsService(GoogleService):

    DOCS_SERVICE_ID = 'docs'
    DOCS_SERVICE_VERSION = 'v1'

    ELEMENTS = 'elements'
    START_INDEX = 'startIndex'
    END_INDEX = 'endIndex'

    PARAGRAPH = 'paragraph'
    HORIZONTAL_RULE = 'horizontalRule'

    TEXT_RUN = 'textRun'
    CONTENT = 'content'

    def __init__(self):
        GoogleService.__init__(self, CREDENTIALS, SCOPES)

    def get_document(self, document_id):
        docs_service = super().get_service(
            self.DOCS_SERVICE_ID,
            self.DOCS_SERVICE_VERSION
        )
        return docs_service.documents().get(documentId=document_id).execute()

    def batch_update(self, document_id, requests):
        docs_service = super().get_service(
            self.DOCS_SERVICE_ID,
            self.DOCS_SERVICE_VERSION
        )
        docs_service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}).execute()

    def get_delete_tokens_requests(self, tokens):
        delete_tokens_requests = []
        for _, tokens in tokens.items():
            delete_tokens_requests.append({
                    'replaceAllText': {
                    'containsText': {
                        'text': '%{}%'.format(tokens['start']),
                        'matchCase':  'true'
                    },
                    'replaceText': '',
                }
            })
            delete_tokens_requests.append({
                    'replaceAllText': {
                    'containsText': {
                        'text': '%{}%'.format(tokens['end']),
                        'matchCase':  'true'
                    },
                    'replaceText': '',
                }
            })
        return delete_tokens_requests

class FilesAPI(DocsService):

    def get_file_rows_from_folder(self,
                                  foldername: str,
                                  filename: str,
                                  rows_range: str):
        file_path = f"/{foldername}/{filename}"
        google_file = super().googledrive_get_file(file_path)

        if google_file is None:
            raise MissingGoogleDriveFileException('Missing file: {}'.format(filename))

        values = super().get_file_values(
            google_file.id,
            rows_range)

        return values

    def empty_document(self, document_id, start_index=0, end_index=0):
        document = super().get_document(document_id)
        content = document.get('body').get('content')
        start_index = self.__get_indext_after_firt_horizontal_rule(content)
        end_index = self.__get_last_end_index(content)

        # Empty file
        if end_index in range(0, 2) or \
            start_index >= end_index:
            return

        requests = [
            {
                'deleteContentRange':{
                    'range': {
                        'segmentId': '',
                        'startIndex': start_index,
                        'endIndex': end_index
                    }
                }
            }
        ]
        super().batch_update(document_id=document_id, requests=requests)

    def insert_eval_report_in_document(self,
                                       eval_process_id,
                                       document_id,
                                       reviewee,
                                       reviewee_evaluations):
        eval_report_with_tokens = self.__build_eval_report_with_tokens(
            eval_process_id,
            reviewee_evaluations)
        self.__insert_eval_report_with_tokens(
            document_id,
            eval_report_with_tokens,
            reviewee)
        self.__apply_eval_report_style(document_id)
        self.__delete_tokens_from_document(document_id)

    def __get_eval_report_style_tokens(self):
        return {
            'eval_title': {
                'start': 'start-eval-title',
                'end': 'end-eval-title'
            },
            'reviewer': {
                'start': 'start-reviewer',
                'end': 'end-reviewer',
            },
            'question': {
                'start': 'start-question',
                'end': 'end-question',
            },
            'answer': {
                'start': 'start-answer',
                'end': 'end-answer',
            },
        }

    def __get_eval_report_style(self, kind, start_index, end_index):
        if kind == 'question':
            return {
                'updateTextStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'textStyle': {
                        'fontSize': {
                            'magnitude': 14,
                            'unit': 'PT'
                        },
                        'bold': False,
                    },
                    'fields': '*'
                }
            }
        elif kind == 'reviewer':
            return {
                'updateTextStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'textStyle': {
                        'fontSize': {
                            'magnitude': 16,
                            'unit': 'PT'
                        },
                        'bold': False,
                    },
                    'fields': '*'
                }
            }
        elif kind == 'eval_title':
            return {
                'updateTextStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'textStyle': {
                        'fontSize': {
                            'magnitude': 20,
                            'unit': 'PT'
                        },
                        'bold': True,
                    },
                    'fields': '*'
                }
            }
        elif kind == 'answer':
            return None
        else:
            raise NotImplementedError("eval report style not implemented")

    def ___build_styled_eval_report_element(self, element, content):
        style_tokens = self.__get_eval_report_style_tokens()
        element_style = style_tokens.get(element, {'start':'', 'end':''})
        return '%{}%{}%{}%'.format(element_style['start'], content, element_style['end'])

    def __build_eval_report_with_tokens(self, eval_process_id, reviewee_evaluations):
        styled_title = self.___build_styled_eval_report_element('eval_title', eval_process_id)
        styled_eval_report = ''

        for reviewer_response in reviewee_evaluations:
            eval_kind = self.__get_human_readable_eval_kind(reviewer_response.eval_kind)
            styled_reviewer = self.___build_styled_eval_report_element(
                'reviewer',
                'Reviewer: %s, kind: %s' % (reviewer_response.reviewer, eval_kind))

            styled_responses = ''
            for question, answer in reviewer_response.eval_response:
                styled_question = self.___build_styled_eval_report_element('question', question)
                styled_answer = self.___build_styled_eval_report_element('answer', answer)
                styled_responses = '{}\n{}\n{}\n'.format(styled_responses, styled_question, styled_answer)

            styled_eval_report = '{}\n\n{}\n{}'.format(styled_eval_report, styled_reviewer, styled_responses)

        return '{}\n{}'.format(styled_title, styled_eval_report)

    def __get_human_readable_eval_kind(self, eval_kind):
        if eval_kind == EvalKind.SELF:
            return 'Self evaluation'
        elif eval_kind == EvalKind.PEER_MANAGER:
            return 'Report by direct report'
        elif eval_kind == EvalKind.MANAGER_PEER:
            return 'Report by direct manager'
        elif eval_kind == EvalKind.PEER_TO_PEER:
            return 'Report by peer'
        else:
            return ''

    def __insert_eval_report_with_tokens(self, document_id, eval_report_with_tokens, reviewee):
        document = super().get_document(document_id)
        content = document.get('body').get('content')
        insert_index = self.__get_indext_after_firt_horizontal_rule(content)

        requests = [
            {
                'insertText': {
                    "text": '\n{{EVAL}}\n',
                    "location": {
                        # object (Location)
                        "index": insert_index,
                    }
                }
            },
            {
                'replaceAllText': {
                    'containsText': {
                        'text': '{{EVAL}}',
                        'matchCase':  'true'
                    },
                    'replaceText': eval_report_with_tokens,
                }
            },
            {
                'replaceAllText': {
                    'containsText': {
                        'text': '{{employee-name}}',
                        'matchCase':  'true'
                    },
                    'replaceText': reviewee,
                },
            }
        ]
        super().batch_update(document_id=document_id, requests=requests)

    def __apply_eval_report_style(self, document_id):
        document = super().get_document(document_id)
        content = document.get('body').get('content')

        style_requests = []
        for item in content:
            if DocsService.PARAGRAPH in item:
                for element in item.get(DocsService.PARAGRAPH).get(DocsService.ELEMENTS):
                    if DocsService.TEXT_RUN in element and DocsService.CONTENT in element.get(DocsService.TEXT_RUN):
                        content = element.get(DocsService.TEXT_RUN).get(DocsService.CONTENT)
                        possible_tokens = content.split('%')

                        for token_uid, tokens in self.__get_eval_report_style_tokens().items():
                            if tokens['start'] in possible_tokens and tokens['end']:
                                start_index = element.get(DocsService.START_INDEX)
                                end_index = element.get(DocsService.END_INDEX)
                                style_request = self.__get_eval_report_style(token_uid, start_index, end_index)
                                if style_request is not None:
                                    style_requests.append(style_request)

        super().batch_update(document_id=document_id, requests=style_requests)

    def __delete_tokens_from_document(self, document_id):
        tokens = self.__get_eval_report_style_tokens()
        delete_token_requests = super().get_delete_tokens_requests(tokens)
        super().batch_update(
            document_id=document_id,
            requests=delete_token_requests)

    def __get_indext_after_firt_horizontal_rule(self, content):
        horizontal_rule_was_seen = False
        for item in content:
            if DocsService.PARAGRAPH in item:
                for element in item.get(DocsService.PARAGRAPH).get(DocsService.ELEMENTS):
                    if DocsService.HORIZONTAL_RULE in element:
                        horizontal_rule_was_seen = True
                        next_index_hr = element.get(DocsService.END_INDEX) + 1

                if horizontal_rule_was_seen:
                    break
        return next_index_hr

    def __get_last_end_index(self, content):
        last_item = content[len(content)-1]
        end_index = 0

        for element in last_item.get(DocsService.PARAGRAPH).get(DocsService.ELEMENTS):
            end_index = element.get(DocsService.START_INDEX)

            if DocsService.TEXT_RUN in element:
                text_run = element.get(DocsService.TEXT_RUN)
                if DocsService.CONTENT in text_run:
                    if text_run.get(DocsService.CONTENT) == '\n':
                        return end_index

        return end_index

class GmailAPI(GmailService):

    AUTHENTICATED_USER = 'me'

    def send_message(self, user_id, message):
        """Send an email message.

        Args:
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

        Returns:
        Sent Message.
        """
        message = super().send_email(
            user_id=user_id,
            body=message
        )
        return message

class GoogleAPI(FilesAPI, GoogleDrive, SheetsService, GmailAPI):
    'Composition of google APIs'

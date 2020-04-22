from __future__ import print_function
from googleapiclient.discovery import build

from auth import GoogleAuth

def get_next_element_in_hr_paragraph(content):
    ELEMENTS = 'elements'
    END_INDEX = 'endIndex'
    PARAGRAPH = 'paragraph'
    HORIZONTAL_RULE = 'horizontalRule'

    horizontal_rule_was_seen = False
    for item in content:
        if PARAGRAPH in item:
            for element in item.get(PARAGRAPH).get(ELEMENTS):
                if HORIZONTAL_RULE in element:
                    horizontal_rule_was_seen = True
                    next_index_hr = element.get(END_INDEX) + 1

            if horizontal_rule_was_seen:
                break
    return next_index_hr


def main():
    current_eval_report = '''%start-eval-title%2020Q1%end-eval-title%

%start-reviewer%Ctanganito%end-reviewer%

%start-question%Do you like trap?%end-question%
%start-answer%Wha%end-answer%

%start-question%What kind of music you like most?%end-question%
%start-answer%answer1%end-answer%

%start-question%If you have to be an animal, what kind of animal you would be?%end-question%
%start-answer%answer1%end-answer%


%start-reviewer%Fulanito%end-reviewer%

%start-question%Do you like trap?%end-question%
%start-answer%What%end-answer%

%start-question%What kind of music you like most?%end-question%
%start-answer%answer1%end-answer%

%start-question%If you have to be an animal, what kind of animal you would be?%end-question%
%start-answer%answer1%end-answer%'''

    creds = GoogleAuth.authenticate()

    docs = build('docs', 'v1', credentials=creds)
    drive = build('drive', 'v3', credentials=creds)

    template_id = 'TEMPLATE_ID'

    # 1.
    # Copy template file for new eval doc
    results = drive.files().copy(
        fileId=template_id,
        body={
            'name': 'Eval Doc: from template',
            'mimeType': 'application/vnd.google-apps.document'
        }
    ).execute()
    document_id = results.get('id')

    # Insert paragraph behind HORIZONTAL_RULE
    document = docs.documents().get(documentId=document_id).execute()
    print('The title of the document is: {}'.format(document.get('title')))

    # 2.
    # Obtaining next element in paragraph to insert text AFTER the first horizontal rule
    content = document.get('body').get('content')
    next_index_hr = get_next_element_in_hr_paragraph(content)

    requests = [
            {
                'insertText': {
                    # object (InsertTextRequest)
                    "text": '\n{{EVAL}}\n',
                    # Union field insertion_location can be only one of the following:
                    "location": {
                        # object (Location)
                        "index": next_index_hr,
                    }
                }
            },
            {
                'replaceAllText': {
                    'containsText': {
                        'text': '{{EVAL}}',
                        'matchCase':  'true'
                    },
                    'replaceText': current_eval_report,
                }
            },
            {
                'replaceAllText': {
                    'containsText': {
                        'text': '{{employee-name}}',
                        'matchCase':  'true'
                    },
                    'replaceText': 'egarcia',
                },
            }
    ]
    results = docs.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

    # 3.
    # Detect tokens and update styles
    document = docs.documents().get(documentId=document_id).execute()
    content = document.get('body').get('content')

    START_INDEX = 'startIndex'
    END_INDEX = 'endIndex'

    ELEMENTS = 'elements'
    TEXT_RUN = 'textRun'
    PARAGRAPH = 'paragraph'

    CONTENT = 'content'

    eval_report_tokens = {
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

    style_requests = []
    for item in content:        
        if PARAGRAPH in item:
            for element in item.get(PARAGRAPH).get(ELEMENTS):
                if TEXT_RUN in element and CONTENT in element.get(TEXT_RUN):
                    content = element.get(TEXT_RUN).get(CONTENT)
                    possible_tokens = content.split('%')

                    for token_uid, tokens in eval_report_tokens.items():
                        if tokens['start'] in possible_tokens and tokens['end']:
                            start_index = element.get(START_INDEX)
                            end_index = element.get(END_INDEX)

                            if token_uid == 'eval_title':
                                style_requests.append({
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
                                })
                            
                            elif token_uid == 'reviewer':
                                style_requests.append({
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
                                })

                            elif token_uid == 'question':
                                style_requests.append({
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
                                })
    docs.documents().batchUpdate(documentId=document_id, body={'requests': style_requests}).execute()

    # 4.
    # Remove tokens
    delete_tokens_requests = [
        {
            'replaceAllText': {
                'containsText': {
                    'text': '%start-eval-title%',
                    'matchCase':  'true'
                },
                'replaceText': '',
            },
        },
        {
            'replaceAllText': {
                'containsText': {
                    'text': '%end-eval-title%',
                    'matchCase':  'true'
                },
                'replaceText': '',
            }
        },
        {
            'replaceAllText': {
                'containsText': {
                    'text': '%start-reviewer%',
                    'matchCase':  'true'
                },
                'replaceText': '',
            }
        },
        {
            'replaceAllText': {
                'containsText': {
                    'text': '%end-reviewer%',
                    'matchCase':  'true'
                },
                'replaceText': '',
            }
        }, {
            'replaceAllText': {
                'containsText': {
                    'text': '%start-question%',
                    'matchCase':  'true'
                },
                'replaceText': '',
            }
        }, {
            'replaceAllText': {
                'containsText': {
                    'text': '%end-question%',
                    'matchCase':  'true'
                },
                'replaceText': '',
            }
        }, {
            'replaceAllText': {
                'containsText': {
                    'text': '%start-answer%',
                    'matchCase':  'true'
                },
                'replaceText': '',
            }
        }, {
            'replaceAllText': {
                'containsText': {
                    'text': '%end-answer%',
                    'matchCase':  'true'
                },
                'replaceText': '',
            }
        }
    ]

    docs.documents().batchUpdate(documentId=document_id, body={'requests': delete_tokens_requests}).execute()

    results = drive.permissions().create(
        fileId=document_id,
        body={
            'type': 'user',
            'emailAddress': 'mail1@company.com',
            'role': 'commenter',
        }
    ).execute()
    print(results)
    results = drive.permissions().create(
        fileId=document_id,
        body={
            'type': 'user',
            'emailAddress': 'mailcompany.com',
            'role': 'commenter',
        }
    ).execute()
    print(results)
    print()
    results = drive.permissions().list(
        fileId=document_id
    ).execute()
    print(results)


if __name__ == '__main__':
    main()

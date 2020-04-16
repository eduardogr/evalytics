from __future__ import print_function
from googleapiclient.discovery import build
import datetime

from auth import GoogleAuth


def main():
    creds = GoogleAuth.authenticate()

    service = build('docs', 'v1', credentials=creds)
    document_id = '1q1X8FfMRN7v-M0i1Pnufct1kQAUsAcAodXzDCZjvnuA'

    # Retrieve the documents contents from the Docs service.
    '''
    title = 'My Evalytics document'
    body = {
        'title': title
    }
    doc = service.documents() \
        .create(body=body).execute()
    print('Created document with title: {0}'.format(
        doc.get('title')))

    print('The title of the document is: {}'.format(doc.get('title')))
    print('The ID of the document is: {}'.format(doc.get('documentId')))
    '''

    customer_name = 'Alice'
    date = datetime.datetime.now().strftime("%y/%m/%d")

    reviews = '''{{start-reviewer}}Ctanganite{{end-reviewer}}
{{start-question}}Do you like trap?{{end-question}}
{{start-answer}}Wha{{end-answer}}

{{start-question}}What kind of music you like most?{{end-question}}
{{start-answer}}answer1{{end-answer}}

{{start-question}}If you have to be an animal, what kind of animal you would be?{{end-question}}
{{start-answer}}answer1{{end-answer}}

{{start-reviewer}}Fulanite{{end-reviewer}}
{{start-question}}Do you like trap?{{end-question}}
{{start-answer}}Wha{{end-answer}}

{{start-question}}What kind of music you like most?{{end-question}}
{{start-answer}}answer1{{end-answer}}

{{start-question}}If you have to be an animal, what kind of animal you would be?{{end-question}}
{{start-answer}}answer1{{end-answer}}'''
    requests = [
            {
                'replaceAllText': {
                    'containsText': {
                        'text': '{{employee-name}}',
                        'matchCase':  'true'
                    },
                    'replaceText': customer_name,
                }
            },
            {
                'replaceAllText': {
                    'containsText': {
                        'text': '{{year-quarter}}',
                        'matchCase':  'true'
                    },
                    'replaceText': '2020 Q1',
                }
            },
            {
                'replaceAllText': {
                    'containsText': {
                        'text': '{{reviews}}',
                        'matchCase':  'true'
                    },
                    'replaceText': reviews,
                }
            }
    ]

    result = service.documents().batchUpdate(
        documentId=document_id, body={'requests': requests}).execute()

    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=document_id).execute()

    print('The title of the document is: {}'.format(document.get('title')))
    content = document.get('body').get('content')

    START_INDEX = 'startIndex'
    END_INDEX = 'endIndex'

    SECTION_BREAK = 'sectionBreak'

    PARAGRAPH = 'paragraph'
    ELEMENTS = 'elements'
    TEXT_RUN = 'textRun'

    CONTENT = 'content'

    TOKENS = {
        'reviewer': {
            'start': '{{start-reviewer}}',
            'end': '{{end-reviewer}}',
        },
        'question': {
            'start': '{{start-question}}',
            'end': '{{end-question}}',
        },
        'answer': {
            'start': '{{start-answer}}',
            'end':  '{{end-answer}}',
        },
    }

    for item in content:
        if PARAGRAPH in item:
            for element in item.get(PARAGRAPH).get(ELEMENTS):
                if TEXT_RUN in element:
                    if CONTENT in element.get(TEXT_RUN):
                        content = element.get(TEXT_RUN).get(CONTENT)
                        if '{{' in content and '}}' in content:
                            print('Indexes: %s-%s' % (
                                element.get(START_INDEX),
                                element.get(END_INDEX)
                            ))
                            print("Elements: [%s]" % (
                                [k for k,v in element.items()]
                            ))

                            print('Content: %s\n' % content)
                    else:
                        print('=========')
                        print(element.get(TEXT_RUN))
                        print('=========')

        elif SECTION_BREAK in item:
            print(item.get(PARAGRAPH))
        else:
            print('something i didnt expect')

    # 1. gather tokens
    # 2. update styles
    # 3. remove tokens

    results = build('drive', 'v3', credentials=creds).permissions().list(
        fileId=document_id
    ).execute()
    print(results)


if __name__ == '__main__':
    main()

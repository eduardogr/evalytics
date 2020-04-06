import tornado.web

import json

from .usecases import SetupUseCase, GetReviewersUseCase
from .models import Reviewer, Employee, EvalKind, Eval

class SetupHandler(tornado.web.RequestHandler):
    path = r"/setup"

    async def post(self):
        try:
            setup_usecase = SetupUseCase()
            setup = setup_usecase.execute()
            self.finish({
                'setup': setup.to_json()
            })
        except:
            self.finish({
                'success': False,
                'message': 'Something went wrong setting up evalytics',
            })

class ReviewersHandler(tornado.web.RequestHandler):
    path = r"/reviewers"

    async def get(self):
        get_reviewers = GetReviewersUseCase()
        reviewers = get_reviewers.execute()

        self.finish({
            'success': True,
            'reviewers': [r.to_json() for uid, r in reviewers.items()]
        })

class SendMailHandler(tornado.web.RequestHandler):
    path = r"/sendmail"

    async def post(self):
        arg_reviewers = json.loads(self.get_argument('reviewers', [], strip=False))

        reviewers = {}
        for reviewer in arg_reviewers:
            employee = reviewer['employee']
            evals = []
            for e in reviewer['evals']:
                evals.append(Eval(
                        reviewee=e['reviewee'],
                        kind=EvalKind.from_str(e['kind']),
                        form=e['form'],
                    )
                )
            employee = Employee(
                    mail=employee['mail'],
                    manager=employee['manager'],
                    area=employee['area']
                )
            reviewers.update({
                employee.uid: Reviewer(
                    employee=employee,
                    evals=evals)
            })

        self.finish({
            'reviewers': [r.to_json() for uid, r in reviewers.items()],
        })

class EvalsHandler(tornado.web.RequestHandler):
    path = r"/evals"

    async def get(self):
        id = str(self.get_argument('id', -1, True))

        self.finish({
            'id': id,
            'eval': {},
        })

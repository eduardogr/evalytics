import json
import sys

import tornado.web

from .usecases import SetupUseCase, GetReviewersUseCase, SendMailUseCase
from .mappers import Mapper


class SetupHandler(tornado.web.RequestHandler):
    path = r"/setup"

    async def post(self):
        try:
            setup_usecase = SetupUseCase()
            setup = setup_usecase.execute()
            self.finish({
                'success': True,
                'setup': setup.to_json()
            })
        except:
            error = sys.exc_info()[0]
            self.finish({
                'success': False,
                'error': { 
                    'message': error,
                }
            })

class ReviewersHandler(tornado.web.RequestHandler):
    path = r"/reviewers"

    async def get(self):
        try:
            get_reviewers = GetReviewersUseCase()
            reviewers = get_reviewers.execute()

            self.finish({
                'success': True,
                'reviewers': [r.to_json() for uid, r in reviewers.items()]
            })
        except:
            error = sys.exc_info()[0]
            self.finish({
                'success': False,
                'error': { 
                    'message': error,
                }
            })

class SendMailHandler(tornado.web.RequestHandler, SendMailUseCase, Mapper):
    path = r"/sendmail"

    async def post(self):
        try:
            reviewer_arg = self.get_argument('reviewers', "[]", strip=False)
            reviewers = super().json_to_reviewer(json.loads(reviewer_arg))

            evals_sent, evals_not_sent = super().send_mail(reviewers)
            self.finish({
                'sucess': True,
                'evals_sent': evals_sent,
                'evals_not_sent': evals_not_sent
            })
        except:
            error = sys.exc_info()[0]
            self.finish({
                'success': False,
                'error': { 
                    'message': error,
                }
            })

class EvalsHandler(tornado.web.RequestHandler):
    path = r"/evals"

    async def get(self):
        try:
            id = str(self.get_argument('id', None, True))
            self.finish({
                'sucess': True,
                'id': id,
                'eval': {},
            })
        except:
            error = sys.exc_info()[0]
            self.finish({
                'success': False,
                'error': { 
                    'message': error,
                }
            })

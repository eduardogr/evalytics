import json
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

class SendMailHandler(tornado.web.RequestHandler, SendMailUseCase, Mapper):
    path = r"/sendmail"

    async def post(self):
        reviewer_arg = self.get_argument('reviewers', "[]", strip=False)
        reviewers = super().json_to_reviewer(json.loads(reviewer_arg))

        reviewers = super().send_mail(reviewers)
        self.finish({
            'reviewers': [r.to_json() for uid, r in reviewers.items()],
        })

class EvalsHandler(tornado.web.RequestHandler):
    path = r"/evals"

    async def get(self):
        id = str(self.get_argument('id', None, True))

        self.finish({
            'id': id,
            'eval': {},
        })

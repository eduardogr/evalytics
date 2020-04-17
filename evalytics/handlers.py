import tornado.web

from .usecases import SetupUseCase, GetReviewersUseCase, SendMailUseCase
from .mappers import Mapper
from .exceptions import MissingDataException, NoFormsException

class SetupHandler(tornado.web.RequestHandler, SetupUseCase):
    path = r"/setup"

    async def post(self):
        try:
            setup = super().setup()
            self.finish({
                'success': True,
                'response': {
                    'setup': setup.to_json()
                }
            })
        except Exception as e:
            if hasattr(e, 'message'):
                message = e.message
            else:
                message = str(e)
            self.finish({
                'success': False,
                'response': {
                    'error': message,
                }
            })

class ReviewersHandler(tornado.web.RequestHandler, GetReviewersUseCase):
    path = r"/reviewers"

    async def get(self):
        try:
            reviewers = super().get_reviewers()

            self.finish({
                'success': True,
                'response': {
                    'reviewers': [r.to_json() for uid, r in reviewers.items()]
                }
            })
        except (MissingDataException, NoFormsException) as exception:
            self.finish({
                'success': False,
                'response': {
                    'error': exception.message,
                }
            })
        except Exception as e:
            if hasattr(e, 'message'):
                message = e.message
            else:
                message = str(e)
            self.finish({
                'success': False,
                'response': {
                    'error': message,
                }
            })

class SendMailHandler(tornado.web.RequestHandler, SendMailUseCase, Mapper):
    path = r"/sendmail"

    async def post(self):
        try:
            reviewers_arg = self.get_argument('reviewers', "[]", strip=False)
            reviewers = super().json_to_reviewers(reviewers_arg)

            evals_sent, evals_not_sent = super().send_mail(reviewers)
            self.finish({
                'success': True,
                'response': {
                    'evals_sent': evals_sent,
                    'evals_not_sent': evals_not_sent
                }
            })
        except Exception as e:
            if hasattr(e, 'message'):
                message = e.message
            else:
                message = str(e)
            self.finish({
                'success': False,
                'response': {
                    'error': message,
                }
            })

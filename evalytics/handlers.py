import tornado.web

from .usecases import SetupUseCase, GetReviewersUseCase, SendMailUseCase
from .usecases import GetResponseStatus
from .mappers import Mapper
from .exceptions import MissingDataException, NoFormsException

class SetupHandler(tornado.web.RequestHandler):
    path = r"/setup"

    async def post(self):
        try:
            setup = SetupUseCase().setup()
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

class ReviewersHandler(tornado.web.RequestHandler):
    path = r"/reviewers"

    async def get(self):
        try:
            reviewers = GetReviewersUseCase().get_reviewers()

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

class SendMailHandler(tornado.web.RequestHandler, Mapper):
    path = r"/sendmail"

    async def post(self):
        try:
            reviewers_arg = self.get_argument('reviewers', "[]", strip=False)
            reviewers = super().json_to_reviewers(reviewers_arg)

            evals_sent, evals_not_sent = SendMailUseCase().send_mail(reviewers)
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

class ResponseStatusHandler(tornado.web.RequestHandler):
    path = r"/status"

    async def get(self):
        try:
            completed, pending, inconsistent = GetResponseStatus().get_response_status()

            self.finish({
                'success': True,
                'response': {
                    'status': {
                        'completed': completed,
                        'pending': pending,
                        'inconsistent': inconsistent
                    }
                }
            })
        except (MissingDataException) as exception:
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
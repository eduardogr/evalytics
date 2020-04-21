import tornado.web

from .usecases import SetupUseCase, GetReviewersUseCase, SendEvalUseCase
from .usecases import GetResponseStatusUseCase
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
    path = r"/evaldelivery"

    async def post(self):
        try:
            reviewers_arg = self.get_argument('reviewers', "[]", strip=False)
            is_reminder_arg = self.get_argument('is_reminder', False, strip=False)

            is_reminder = super().json_to_bool(is_reminder_arg)
            reviewers = super().json_to_reviewers(reviewers_arg)

            evals_sent, evals_not_sent = SendEvalUseCase().send_eval(reviewers, is_reminder=is_reminder)
            self.finish({
                'success': True,
                'response': {
                    'is_reminder': is_reminder,
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
            completed, pending, inconsistent = GetResponseStatusUseCase().get_response_status()

            self.finish({
                'success': True,
                'response': {
                    'status': {
                        'completed': completed,
                        'pending': [r.to_json() for uid, r in pending.items()],
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

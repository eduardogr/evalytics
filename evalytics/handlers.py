import tornado.web

from evalytics.usecases import SetupUseCase, GetReviewersUseCase
from evalytics.usecases import GetResponseStatusUseCase, GenerateEvalReportsUseCase
from evalytics.usecases import GetPeersAssignmentUseCase, UpdatePeersAssignmentUseCase
from evalytics.usecases import SendCommunicationUseCase
from evalytics.mappers import Mapper
from evalytics.exceptions import MissingDataException, NoFormsException
from evalytics.exceptions import GoogleApiClientHttpErrorException

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

class CommunicationHandler(tornado.web.RequestHandler, Mapper):
    path = r"/communications"

    async def post(self):
        try:
            reviewers_arg = self.get_argument('reviewers', "[]", strip=False)
            kind_arg = self.get_argument('kind', "", strip=False)

            reviewers = super().json_to_reviewers(reviewers_arg)
            kind = super().string_to_communication_kind(kind_arg)

            comms_sent, comms_not_sent = SendCommunicationUseCase().send(reviewers, kind=kind)
            self.finish({
                'success': True,
                'response': {
                    'comms_sent': comms_sent,
                    'comms_not_sent': comms_not_sent
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

class EvalReportsHandler(tornado.web.RequestHandler, Mapper):
    path = r"/evalreports"

    async def post(self):
        try:
            eval_process_id = self.get_argument('eval_process_id', 'EVAL_ID', strip=False)

            area = self.get_argument('area', None, strip=False)
            managers_arg = self.get_argument('managers', None, strip=False)
            employee_uids_arg = self.get_argument('uids', None, strip=False)

            dry_run_arg = self.get_argument('dry_run', 'False', strip=False)

            managers = super().json_to_list(managers_arg)
            employee_uids = super().json_to_list(employee_uids_arg)
            dry_run = super().str_to_bool(dry_run_arg)
            
            created, not_created = GenerateEvalReportsUseCase().generate(
                dry_run,
                eval_process_id,
                area,
                managers,
                employee_uids
            )

            self.finish({
                'success': True,
                'response': {
                    'evals_reports': {
                        'created': created,
                        'not_created': not_created,
                    }
                }
            })
        except MissingDataException as e:
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

class PeersAssignmentHandler(tornado.web.RequestHandler, Mapper):
    path = r"/peers"

    async def get(self):
        try:

            peers_assignment = GetPeersAssignmentUseCase().get_peers()

            self.finish({
                'success': True,
                'response': {
                    'peers_assignment': peers_assignment
                }
            })
        except MissingDataException as e:
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
        except GoogleApiClientHttpErrorException as e:
            self.finish({
                'success': False,
                'response': e.get_google_api_client_http_error().to_json()
            })

    async def post(self):
        try:

            peers_assignment, unanswered_forms = UpdatePeersAssignmentUseCase().update()

            self.finish({
                'success': True,
                'response': {
                    'peers_assignment': peers_assignment,
                    'unanswered_forms': unanswered_forms
                }
            })
        except MissingDataException as e:
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
        except GoogleApiClientHttpErrorException as e:
            self.finish({
                'success': False,
                'response': e.get_google_api_client_http_error().to_json()
            })

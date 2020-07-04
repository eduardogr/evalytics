import tornado.web

from evalytics.usecases import SetupUseCase, GetReviewersUseCase
from evalytics.usecases import GetEmployeesUseCase, GetSurveysUseCase
from evalytics.usecases import GetResponseStatusUseCase
from evalytics.usecases import GenerateEvalReportsUseCase
from evalytics.usecases import GetPeersAssignmentUseCase
from evalytics.usecases import UpdatePeersAssignmentUseCase
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
                    'setup': Mapper().google_setup_to_json(setup)
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

class EmployeesHandler(tornado.web.RequestHandler):
    path = r"/employees"

    async def get(self):
        try:
            employees = GetEmployeesUseCase().get_employees()

            self.finish({
                'success': True,
                'response': {
                    'employees': [Mapper().employee_to_json(e) for uid, e in employees.items()]
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

class SurveysHandler(tornado.web.RequestHandler):
    path = r"/surveys"

    async def get(self):
        try:
            surveys = GetSurveysUseCase().get_surveys()

            self.finish({
                'success': True,
                'response': {
                    'surveys': surveys
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

class PeersAssignmentHandler(tornado.web.RequestHandler):
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
            error = e.get_google_api_client_http_error()
            self.finish({
                'success': False,
                'response': Mapper().google_api_client_http_error_to_json(error)
            })

    async def post(self):
        try:

            peers_assignment = UpdatePeersAssignmentUseCase().update()

            self.finish({
                'success': True,
                'response': {
                    'peers_assignment': peers_assignment.peers,
                    'unanswered_forms': peers_assignment.unanswered_forms
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
            error = e.get_google_api_client_http_error()
            self.finish({
                'success': False,
                'response': Mapper().google_api_client_http_error_to_json(error)
            })

class ReviewersHandler(tornado.web.RequestHandler):
    path = r"/reviewers"

    async def get(self):
        try:
            reviewers = GetReviewersUseCase().get_reviewers()

            self.finish({
                'success': True,
                'response': {
                    'reviewers': [Mapper().reviewer_to_json(r) for uid, r in reviewers.items()]
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

class CommunicationHandler(tornado.web.RequestHandler):
    path = r"/communications"

    async def post(self):
        try:
            reviewers_arg = self.get_argument('reviewers', "[]", strip=False)
            kind_arg = self.get_argument('kind', "", strip=False)

            reviewers = Mapper().json_to_reviewers(reviewers_arg)
            kind = Mapper().string_to_communication_kind(kind_arg)

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
                        'pending': [Mapper().reviewer_to_json(r) for uid, r in pending.items()],
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

class EvalReportsHandler(tornado.web.RequestHandler):
    path = r"/evalreports"

    async def post(self):
        try:
            area = self.get_argument('area', None, strip=False)
            managers_arg = self.get_argument('managers', None, strip=False)
            employee_uids_arg = self.get_argument('uids', None, strip=False)

            dry_run_arg = self.get_argument('dry_run', 'False', strip=False)

            managers = Mapper().json_to_list(managers_arg)
            employee_uids = Mapper().json_to_list(employee_uids_arg)
            dry_run = Mapper().str_to_bool(dry_run_arg)

            created, not_created = GenerateEvalReportsUseCase().generate(
                dry_run,
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

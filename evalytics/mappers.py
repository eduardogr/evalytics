import json

from evalytics.models import GoogleFile
from evalytics.models import EvalKind, Eval, Employee, Reviewer
from evalytics.models import ReviewerResponse
from evalytics.models import CommunicationKind
from evalytics.models import GoogleApiClientHttpError
from evalytics.config import Config

class StrToBool:

    def str_to_bool(self, str_bool: str):
        true_strings = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
        return str_bool.lower() in true_strings

class JsonToList:

    def json_to_list(self, json_list):
        if json_list is None:
            return None

        if isinstance(json_list, str):
            json_list = json.loads(json_list)

        return json_list

class ListToJson:
    def list_to_json(self, some_list):
        return json.dumps(
            some_list,
            default=lambda o:
            o.__dict__ if type(o) is not EvalKind else str(o.name))

class GoogleFileDictToGoogleFile:

    def google_file_dict_to_google_file(self, google_file_dict):
        if google_file_dict is None:
            return None

        return GoogleFile(
            name=google_file_dict.get('name'),
            id=google_file_dict.get('id'),
            parents=google_file_dict.get('parents'),
        )

class GoogleFileToJson(ListToJson):

    def google_file_to_json(self, google_file: GoogleFile):
        return {
            'name': google_file.name,
            'id': google_file.id,
            'parents': super().list_to_json(google_file.parents)
        }

class EvalToJson:

    def eval_to_json(self, evaluation: Eval):
        return {
            "reviewee": evaluation.reviewee,
            "kind": evaluation.kind.name,
            "form": evaluation.form
        }

class EmployeeToJson:

    def employee_to_json(self, employee: Employee):
        return {
            "mail": employee.mail,
            "uid": employee.uid,
            "manager": employee.manager,
            "area": employee.area,
        }

class ReviewerToJson(EmployeeToJson, EvalToJson):

    def reviewer_to_json(self, reviewer: Reviewer):
        return {
            "employee": super().employee_to_json(reviewer.employee),
            "evals": list(map(super().eval_to_json, reviewer.evals))
        }

class ReviewerResponseToJson:

    def reviewer_response_to_json(self, reviewer_response: ReviewerResponse):
        return {
            'reviewee': reviewer_response.reviewee,
            'reviewer': reviewer_response.reviewer,
            'eval_kind': reviewer_response.eval_kind.name,
            'eval_response': reviewer_response.eval_response
        }

class GoogleApiClientHttpErrorToJson:

    def google_api_client_http_error_to_json(
            self,
            error: GoogleApiClientHttpError):
        return {
            "code": error.code,
            "message": error.message,
            "status": error.status,
            "details": error.details,
        }

class JsonToReviewer:

    def json_to_reviewers(self, json_reviewers):
        if isinstance(json_reviewers, str):
            json_reviewers = json.loads(json_reviewers)

        reviewers = {}
        for reviewer in json_reviewers:
            employee = reviewer['employee']
            evals = []
            for e in reviewer['evals']:
                evals.append(Eval(
                    reviewee=e['reviewee'],
                    kind=EvalKind.from_str(e['kind']),
                    form=e['form'],
                ))
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
        return reviewers

class ReviewerToJsonObject:

    def reviewer_to_json_object(self, reviewers):
        return json.dumps(
            reviewers,
            default=lambda o:
            o.__dict__ if type(o) is not EvalKind else str(o.name))

class StrToCommunicationKind:

    def string_to_communication_kind(self, communication_kind: str):
        return CommunicationKind.from_str(communication_kind)

class ResponseFileNameToEvalKind(Config):

    def response_file_name_to_eval_kind(self, filename):

        if filename.startswith(super().read_google_manager_eval_by_report_prefix()):
            return EvalKind.PEER_MANAGER

        elif filename.startswith(super().read_google_report_eval_by_manager_prefix()):
            return EvalKind.MANAGER_PEER

        elif filename.startswith(super().read_google_peer_eval_by_peer_prefix()):
            return EvalKind.PEER_TO_PEER

        elif filename.startswith(super().read_google_self_eval_prefix()):
            return EvalKind.SELF

        else:
            return None

class Mapper(
        GoogleApiClientHttpErrorToJson,
        ReviewerToJson,
        ReviewerResponseToJson,
        JsonToReviewer,
        ReviewerToJsonObject,
        StrToBool,
        JsonToList,
        ListToJson,
        StrToCommunicationKind,
        GoogleFileDictToGoogleFile,
        ResponseFileNameToEvalKind):
    'Composition of Mappers'

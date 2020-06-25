import json

from evalytics.models import Reviewer, Employee, EvalKind, Eval
from evalytics.models import CommunicationKind

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

class ReviewerToJson:

    def reviewer_to_json(self, reviewers):
        return json.dumps(
            reviewers,
            default=lambda o:
            o.__dict__ if type(o) is not EvalKind else str(o.name))

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

class StrToCommunicationKind:

    def string_to_communication_kind(self, communication_kind: str):
        return CommunicationKind.from_str(communication_kind)

class Mapper(
        JsonToReviewer,
        ReviewerToJson,
        StrToBool,
        JsonToList,
        ListToJson,
        StrToCommunicationKind):
    'Composition of Mappers'

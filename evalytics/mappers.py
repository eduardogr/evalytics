import json

from evalytics.models import Reviewer, Employee, EvalKind, Eval

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

    def str_to_bool(self, str_bool: str):
        true_strings = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
        return str_bool.lower() in true_strings

    def json_to_list(self, json_list):
        if json_list is None:
            return None

        if isinstance(json_list, str):
            json_list = json.loads(json_list)

        return json_list
    
    def list_to_json(self, some_list):
        return json.dumps(
            some_list,
            default=lambda o:
            o.__dict__ if type(o) is not EvalKind else str(o.name))

class ReviewerToJson:

    def reviewer_to_json(self, reviewers):
        return json.dumps(
            reviewers,
            default=lambda o:
            o.__dict__ if type(o) is not EvalKind else str(o.name))

class Mapper(JsonToReviewer, ReviewerToJson):
    'Composition of Mappers'

import json

from .models import Reviewer, Employee, EvalKind, Eval

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

    def json_to_bool(self, json_bool):
        true_strings = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
        return json_bool.lower() in true_strings

    def json_to_list(self, json_list):
        return json.loads(json_list)

class ReviewerToJson:

    def reviewer_to_json(self, reviewers):
        return json.dumps(
            reviewers,
            default=lambda o:
            o.__dict__ if type(o) is not EvalKind else str(o.name))

class Mapper(JsonToReviewer, ReviewerToJson):
    'Composition of Mappers'

import json

from .models import Reviewer, Employee, EvalKind, Eval

class JsonToReviewer:

    def json_to_reviewers(self, json_reviewers):
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

class Mapper(JsonToReviewer, ReviewerToJson):
    'Composition of Mappers'

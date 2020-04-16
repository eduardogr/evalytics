from unittest import TestCase

from evalytics.mappers import JsonToReviewer, ReviewerToJson
from evalytics.models import Reviewer, Employee, Eval, EvalKind

class TestMappers(TestCase):

    def setUp(self):
        employee = Employee(
            mail='mail@mail',
            manager='manager',
            area='Area'
        )
        evals = [
            Eval(reviewee='jaime', kind=EvalKind.SELF, form="finalform")
        ]

        self.json_reviewer_with_no_evals = '{"employee": {"mail": "mail@mail", "manager": "manager", "area": "Area"}, "evals": []}'
        self.jsondict_reviewer_with_no_evals = {
            'employee': {
                'mail': 'mail@mail@mail',
                'manager': 'manager',
                'area': 'area'
            },
            'evals': []
        }

        self.json_reviewer_with_evals = '{"employee": {"mail": "mail@mail", "manager": "manager", "area": "Area"}, "evals": [{"reviewee": "jaime", "kind": "SELF", "form": "finalform"}]}'
        self.jsondict_reviewer_with_evals = {
            'employee': {
                'mail': 'mail@mail@mail',
                'manager': 'manager',
                'area': 'area'
            },
            'evals': [
                {
                    'reviewee': 'jaime',
                    'kind': 'SELF',
                    'form': 'finalform'
                }
            ]
        }

        self.reviewer_with_no_evals = Reviewer(
            employee=employee,
            evals=[]
        )
        self.reviewer_with_evals = Reviewer(
            employee=employee,
            evals=evals
        )

    def test_json_to_reviewer_with_no_evals(self):
        reviewer = JsonToReviewer().json_to_reviewer([self.jsondict_reviewer_with_no_evals])

        self.assertEqual(self.reviewer_with_no_evals, reviewer['mail'])


    def test_json_to_reviewer_with_evals(self):
        reviewer = JsonToReviewer().json_to_reviewer([self.jsondict_reviewer_with_evals])

        self.assertEqual(self.reviewer_with_evals, reviewer['mail'])

    def test_reviewer_to_json_with_no_evals(self):
        json = ReviewerToJson().reviewer_to_json(self.reviewer_with_no_evals)

        self.assertEqual(self.json_reviewer_with_no_evals, json)
    
    def test_reviewer_to_with_evals(self):
        json = ReviewerToJson().reviewer_to_json(self.reviewer_with_evals)

        self.assertEqual(self.json_reviewer_with_evals, json)

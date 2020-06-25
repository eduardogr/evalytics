from unittest import TestCase

from evalytics.mappers import JsonToReviewer, ReviewerToJson
from evalytics.mappers import StrToBool, JsonToList, ListToJson
from evalytics.models import Reviewer, Employee, Eval, EvalKind

class TestJsonToReviewer(TestCase):

    def setUp(self):
        self.sut = JsonToReviewer()
        employee = Employee(
            mail='mail@mail',
            manager='manager',
            area='Area'
        )
        evals = [
            Eval(reviewee='jaime', kind=EvalKind.SELF, form="finalform")
        ]

        self.json_reviewer_with_no_evals = '{"employee": {"mail": "mail@mail", "manager": "manager", "area": "Area"}, "evals": []}'
        self.json_reviewer_with_evals = '{"employee": {"mail": "mail@mail", "manager": "manager", "area": "Area"}, "evals": [{"reviewee": "jaime", "kind": "SELF", "form": "finalform"}]}'
        self.jsondict_reviewer_with_evals = {
            "employee": {
                "mail": "mail@mail@mail",
                "manager": "manager",
                "area": "area"
            },
            "evals": [
                {"reviewee": "jaime","kind": "SELF","form": "finalform"}
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

    def test_jsondict_to_reviewer_with_evals(self):
        reviewer = self.sut.json_to_reviewers([self.jsondict_reviewer_with_evals])

        self.assertEqual(self.reviewer_with_no_evals, reviewer['mail'])

    def test_json_to_reviewer_with_no_evals(self):
        json_reviewers = "[%s]" % self.json_reviewer_with_no_evals
        reviewer = self.sut.json_to_reviewers(json_reviewers)

        self.assertEqual(self.reviewer_with_no_evals, reviewer['mail'])

    def test_json_to_reviewer_with_evals(self):
        json_reviewers = "[%s]" % self.json_reviewer_with_evals
        reviewer = self.sut.json_to_reviewers(json_reviewers)

        self.assertEqual(self.reviewer_with_evals, reviewer['mail'])

class TestReviewerToJson(TestCase):

    def setUp(self):
        self.sut = ReviewerToJson()
        employee = Employee(
            mail='mail@mail',
            manager='manager',
            area='Area'
        )
        evals = [
            Eval(reviewee='jaime', kind=EvalKind.SELF, form="finalform")
        ]

        self.json_reviewer_with_no_evals = '{"employee": {"mail": "mail@mail", "manager": "manager", "area": "Area"}, "evals": []}'
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

    def test_reviewer_to_json_with_no_evals(self):
        json = self.sut.reviewer_to_json(self.reviewer_with_no_evals)

        self.assertEqual(self.json_reviewer_with_no_evals, json)

    def test_reviewer_to_with_evals(self):
        json = self.sut.reviewer_to_json(self.reviewer_with_evals)

        self.assertEqual(self.json_reviewer_with_evals, json)

class TestStrToBool(TestCase):

    def setUp(self):
        self.sut = StrToBool()

    def test_str_to_bool_when_true(self):
        json_bool = "True"

        result = self.sut.str_to_bool(json_bool)

        self.assertEqual(True, result)

    def test_str_to_bool_when_false(self):
        json_bool = "anything not true"

        result = self.sut.str_to_bool(json_bool)

        self.assertEqual(False, result)

class TestJsonToList(TestCase):

    def setUp(self):
        self.sut = JsonToList()

    def test_json_to_list(self):
        json_list = "[1,2,3,4]"

        result = self.sut.json_to_list(json_list)

        self.assertEqual([1, 2, 3, 4], result)

    def test_json_to_list_when_none(self):
        json_list = None

        result = self.sut.json_to_list(json_list)

        self.assertEqual(None, result)

    def test_json_to_list_when_is_an_integer(self):
        json_list = 3

        result = self.sut.json_to_list(json_list)

        self.assertEqual(3, result)

class TestListToJson(TestCase):

    def setUp(self):
        self.sut = ListToJson()

    def test_list_to_json(self):
        list_to_convert = [1, 2, 3, 4]

        result = self.sut.list_to_json(list_to_convert)

        self.assertEqual('[1, 2, 3, 4]', result)

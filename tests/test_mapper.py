from unittest import TestCase

from evalytics.mappers import GoogleFileToJson
from evalytics.mappers import EvalToJson, EmployeeToJson, ReviewerToJson
from evalytics.mappers import ReviewerResponseToJson
from evalytics.mappers import GoogleApiClientHttpErrorToJson
from evalytics.mappers import JsonToReviewer, ReviewerToJsonObject
from evalytics.mappers import StrToBool, JsonToList, ListToJson
from evalytics.mappers import ResponseFileNameToEvalKind

from evalytics.models import Reviewer, Employee, Eval, EvalKind

from tests.common.fixture import Fixture
from tests.common.mocks import MockConfig

class TestGoogleFileToJson(TestCase):

    def test_to_json(self):
        # given:
        google_file = Fixture().get_any_google_file_model()
        expected_json_dict = {
            'name': google_file.name,
            'id': google_file.id,
            'parents': '[]'
        }
        sut = GoogleFileToJson()

        # when:
        json_dict = sut.google_file_to_json(google_file)

        # then:
        self.assertEqual(expected_json_dict, json_dict)

class TestEvalToJson(TestCase):

    def test_to_json(self):
        # given:
        evaluation = Fixture().get_any_eval_model()
        expected_json_dict = {
            'reviewee': evaluation.reviewee,
            'kind': evaluation.kind.name,
            'form': evaluation.form,
        }
        sut = EvalToJson()

        # when:
        json_dict = sut.eval_to_json(evaluation)

        # then:
        self.assertEqual(expected_json_dict, json_dict)

class TestEmployeeToJson(TestCase):

    def test_to_json(self):
        # given:
        employee = Fixture().get_any_employee_model()
        expected_json_dict = {
            'mail': employee.mail,
            'uid': employee.uid,
            'manager': employee.manager,
            'area': employee.area,
        }
        sut = EmployeeToJson()

        # when:
        json_dict = sut.employee_to_json(employee)

        # then:
        self.assertEqual(expected_json_dict, json_dict)

class TestReviewerToJson(TestCase):

    def test_to_json(self):
        # given:
        reviewer = Fixture().get_any_reviewer_model()
        expected_json_dict = {
            'employee': {
                'mail': reviewer.employee.mail,
                'uid': reviewer.employee.uid,
                'manager': reviewer.employee.manager,
                'area': reviewer.employee.area,
            },
            'evals': []
        }
        sut = ReviewerToJson()

        # when:
        json_dict = sut.reviewer_to_json(reviewer)

        # then:
        self.assertEqual(expected_json_dict, json_dict)

class TestReviewerResponseToJson(TestCase):

    def test_to_json(self):
        # given:
        reviewer_response = Fixture().get_any_reviewer_response_model()
        expected_json_dict = {
            'reviewee': reviewer_response.reviewee,
            'reviewer': reviewer_response.reviewer,
            'eval_kind': reviewer_response.eval_kind.name,
            'eval_response': reviewer_response.eval_response
        }
        sut = ReviewerResponseToJson()

        # when:
        json_dict = sut.reviewer_response_to_json(reviewer_response)

        # then:
        self.assertEqual(expected_json_dict, json_dict)

class TestGoogleApiClientHttpErrorToJson(TestCase):

    def test_to_json(self):
        # given:
        google_http_error = Fixture().get_any_google_api_client_http_error__model()
        expected_json_dict = {
            'code': google_http_error.code,
            'message': google_http_error.message,
            'status': google_http_error.status,
            'details': google_http_error.details,
        }
        sut = GoogleApiClientHttpErrorToJson()

        # when:
        json_dict = sut.google_api_client_http_error_to_json(google_http_error)

        # then:
        self.assertEqual(expected_json_dict, json_dict)

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

class TestReviewerToJsonObject(TestCase):

    def setUp(self):
        self.sut = ReviewerToJsonObject()
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
        json = self.sut.reviewer_to_json_object(self.reviewer_with_no_evals)

        self.assertEqual(self.json_reviewer_with_no_evals, json)

    def test_reviewer_to_with_evals(self):
        json = self.sut.reviewer_to_json_object(self.reviewer_with_evals)

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

class ResponseFileNameToEvalKindSut(ResponseFileNameToEvalKind, MockConfig):
    'Inject a mock into ResponseFileNameToEvalKind dependency'

class TestResponseFileNameToEvalKind(TestCase):

    def setUp(self):
        self.sut = ResponseFileNameToEvalKindSut()

    def test_response_file_name_to_eval_kind_when_peer_manager(self):
        # given:
        filename = 'MANAGER EVAL BY REPORT'
        expected_eval_kind = EvalKind.PEER_MANAGER

        # when:
        eval_kind = self.sut.response_file_name_to_eval_kind(filename)

        # then:
        self.assertEqual(expected_eval_kind, eval_kind)

    def test_response_file_name_to_eval_kind_when_manager_peer(self):
        # given:
        filename = 'REPORT EVAL BY MANAGER'
        expected_eval_kind = EvalKind.MANAGER_PEER

        # when:
        eval_kind = self.sut.response_file_name_to_eval_kind(filename)

        # then:
        self.assertEqual(expected_eval_kind, eval_kind)

    def test_response_file_name_to_eval_kind_when_peer_peer(self):
        # given:
        filename = 'PEER EVAL BY PEER'
        expected_eval_kind = EvalKind.PEER_TO_PEER

        # when:
        eval_kind = self.sut.response_file_name_to_eval_kind(filename)

        # then:
        self.assertEqual(expected_eval_kind, eval_kind)

    def test_response_file_name_to_eval_kind_when_self(self):
        # given:
        filename = 'SELF EVAL'
        expected_eval_kind = EvalKind.SELF

        # when:
        eval_kind = self.sut.response_file_name_to_eval_kind(filename)

        # then:
        self.assertEqual(expected_eval_kind, eval_kind)

    def test_response_file_name_to_eval_kind_when_none(self):
        # when:
        eval_kind = self.sut.response_file_name_to_eval_kind('NOO FILENAME')

        # then:
        self.assertEqual(None, eval_kind)

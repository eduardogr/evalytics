from unittest import TestCase

from evalytics.filters import ReviewerResponseFilter
from evalytics.models import ReviewerResponse, Employee
from evalytics.exceptions import NotExistentEmployeeException

class TestReviewerResponseFilter(TestCase):

    def test_no_filter(self):
        any_reviewer_response = ReviewerResponse(
            reviewee='',
            reviewer='',
            eval_kind=None,
            filename='',
            eval_response=[],
            line_number=0
        )
        evaluations = {
            'uid+1': [
                any_reviewer_response,
            ],
            'uid+2': [
                any_reviewer_response,
            ],
            'uid+3': [
                any_reviewer_response,
            ]
        }
        employees = {}
        area = None
        managers = None
        allowed_uids = None

        sut = ReviewerResponseFilter()

        result = sut.filter_reviewees(
                        evaluations,
                        employees,
                        area,
                        managers,
                        allowed_uids)

        self.assertEqual(3, len(result))

    def test_filter_by_uids(self):
        any_reviewer_response = ReviewerResponse(
            reviewee='',
            reviewer='',
            eval_kind=None,
            filename='',
            eval_response=[],
            line_number=0
        )
        evaluations = {
            'uid+1': [
                any_reviewer_response,
            ],
            'uid+2': [
                any_reviewer_response,
            ],
            'uid+3': [
                any_reviewer_response,
            ]
        }
        employees = {}
        area = None
        managers = None
        allowed_uids = ['uid+2']

        sut = ReviewerResponseFilter()

        result = sut.filter_reviewees(
                        evaluations,
                        employees,
                        area,
                        managers,
                        allowed_uids)

        self.assertEqual(1, len(result))

    def test_filter_by_area(self):
        any_reviewer_response = ReviewerResponse(
            reviewee='',
            reviewer='',
            eval_kind=None,
            filename='',
            eval_response=[],
            line_number=0
        )
        evaluations = {
            'uid+1': [
                any_reviewer_response,
            ],
            'uid+2': [
                any_reviewer_response,
            ],
            'uid+3': [
                any_reviewer_response,
            ]
        }
        employees = {
            'uid+1': Employee(mail='uid+1@company.com', manager='boss', area='Eng'),
            'uid+2': Employee(mail='uid+2@company.com', manager='another', area='Product'),
            'uid+3': Employee(mail='uid+2@company.com', manager='another', area='Eng'),
        }
        area = 'Eng'
        managers = None
        allowed_uids = None

        sut = ReviewerResponseFilter()

        result = sut.filter_reviewees(
                        evaluations,
                        employees,
                        area,
                        managers,
                        allowed_uids)

        self.assertEqual(2, len(result))

    def test_filter_by_area_when_employee_does_not_exist(self):
        any_reviewer_response = ReviewerResponse(
            reviewee='',
            reviewer='',
            eval_kind=None,
            filename='',
            eval_response=[],
            line_number=0
        )
        evaluations = {
            'uid+1': [
                any_reviewer_response,
            ]
        }
        employees = {
            'uid+2': Employee(mail='uid+2@company.com', manager='another', area='Product'),
        }
        area = 'Eng'
        managers = None
        allowed_uids = None

        sut = ReviewerResponseFilter()

        with self.assertRaises(NotExistentEmployeeException):
            sut.filter_reviewees(
                evaluations,
                employees,
                area,
                managers,
                allowed_uids)

    def test_filter_by_managers(self):
        any_reviewer_response = ReviewerResponse(
            reviewee='',
            reviewer='',
            eval_kind=None,
            filename='',
            eval_response=[],
            line_number=0
        )
        evaluations = {
            'uid+1': [
                any_reviewer_response,
            ],
            'uid+2': [
                any_reviewer_response,
            ],
            'uid+3': [
                any_reviewer_response,
            ]
        }
        employees = {
            'uid+1': Employee(mail='uid+1@company.com', manager='boss', area='Eng'),
            'uid+2': Employee(mail='uid+2@company.com', manager='another', area='Eng'),
            'uid+3': Employee(mail='uid+2@company.com', manager='another', area='Eng'),
        }
        area = None
        managers = ['boss']
        allowed_uids = None

        sut = ReviewerResponseFilter()

        result = sut.filter_reviewees(
                        evaluations,
                        employees,
                        area,
                        managers,
                        allowed_uids)

        self.assertEqual(1, len(result))

    def test_filter_by_managers_when_employee_does_not_exist(self):
        any_reviewer_response = ReviewerResponse(
            reviewee='',
            reviewer='',
            eval_kind=None,
            filename='',
            eval_response=[],
            line_number=0
        )
        evaluations = {
            'uid+1': [
                any_reviewer_response,
            ]
        }
        employees = {
            'uid+3': Employee(mail='uid+2@company.com', manager='another', area='Eng'),
        }
        area = None
        managers = ['boss']
        allowed_uids = None

        sut = ReviewerResponseFilter()

        with self.assertRaises(NotExistentEmployeeException):
            sut.filter_reviewees(
                evaluations,
                employees,
                area,
                managers,
                allowed_uids)

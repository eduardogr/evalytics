from unittest import TestCase

from evalytics.filters import ReviewerResponseFilter
from evalytics.models import ReviewerResponse

class TestReviewerResponseFilter(TestCase):

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

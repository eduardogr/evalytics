from unittest import TestCase

from ..server.adapters import OrgChartAdapter
from ..server.models import Employee, Eval, EvalSuite, EvalType, OrgChart

# fixtures
jane = Employee('jane@tuenti.com')
jhon = Employee('jhon@tuenti.com', supervisor=jane)
minion_1 = Employee('minion1@tuenti.com', supervisor=jhon)
minion_2 = Employee('minion2@tuenti.com', supervisor=jhon)
minion_3 = Employee('minion3@tuenti.com', supervisor=jhon)
org_chart = OrgChart(jane)


class TestOrgChartAdapter(TestCase):

    def setUp(self):
        self.org_chart_adapter = OrgChartAdapter()  # subject

    def test_create_initial_180_eval_suite(self):
        initial_eval_suite = self.org_chart_adapter.create_initial_eval_suite(
            org_chart)

        self.assertListEqual(initial_eval_suite.evals, [
            Eval(jane, jane, EvalType.SELF),
            Eval(jane, jhon, EvalType.MY_MINION),
            Eval(jhon, jhon, EvalType.SELF),
            Eval(jhon, jane, EvalType.MY_SUPERVISOR),
            Eval(jhon, minion_1, EvalType.MY_MINION),
            Eval(jhon, minion_2, EvalType.MY_MINION),
            Eval(jhon, minion_3, EvalType.MY_MINION),
            Eval(minion_1, minion_1, EvalType.SELF),
            Eval(minion_1, jhon, EvalType.MY_SUPERVISOR),
            Eval(minion_2, minion_2, EvalType.SELF),
            Eval(minion_2, jhon, EvalType.MY_SUPERVISOR),
            Eval(minion_3, minion_3, EvalType.SELF),
            Eval(minion_3, jhon, EvalType.MY_SUPERVISOR),
        ])

    def test_create_initial_180_eval_suite_considering_peers(self):
        initial_eval_suite = self.org_chart_adapter.create_initial_eval_suite(
            org_chart, consider_peers=True)

        self.assertListEqual(initial_eval_suite.evals, [
            Eval(jane, jane, EvalType.SELF),
            Eval(jane, jhon, EvalType.MY_MINION),
            Eval(jhon, jhon, EvalType.SELF),
            Eval(jhon, jane, EvalType.MY_SUPERVISOR),
            Eval(jhon, minion_1, EvalType.MY_MINION),
            Eval(jhon, minion_2, EvalType.MY_MINION),
            Eval(jhon, minion_3, EvalType.MY_MINION),
            Eval(minion_1, minion_1, EvalType.SELF),
            Eval(minion_1, jhon, EvalType.MY_SUPERVISOR),
            Eval(minion_1, minion_2, EvalType.PEER),
            Eval(minion_1, minion_3, EvalType.PEER),
            Eval(minion_2, minion_2, EvalType.SELF),
            Eval(minion_2, jhon, EvalType.MY_SUPERVISOR),
            Eval(minion_2, minion_1, EvalType.PEER),
            Eval(minion_2, minion_3, EvalType.PEER),
            Eval(minion_3, minion_3, EvalType.SELF),
            Eval(minion_3, jhon, EvalType.MY_SUPERVISOR),
            Eval(minion_3, minion_1, EvalType.PEER),
            Eval(minion_3, minion_2, EvalType.PEER),
        ])

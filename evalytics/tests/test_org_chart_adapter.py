from unittest import TestCase

from evalytics.server.adapters import OrgChartAdapter
from evalytics.server.models import Eval, EvalType, OrgChart
from evalytics.tests.fixtures import employees


class TestOrgChartAdapter(TestCase):

    def setUp(self):
        self.org_chart = OrgChart(employees.jane)
        self.org_chart_adapter = OrgChartAdapter()  # subject

    def test_create_initial_180_eval_suite(self):
        initial_eval_suite = self.org_chart_adapter.create_initial_eval_suite(
            self.org_chart)

        self.assertListEqual(initial_eval_suite.evals, [
            Eval(employees.jane, employees.jane, EvalType.SELF),
            Eval(employees.jane, employees.jhon, EvalType.MY_MINION),
            Eval(employees.jhon, employees.jhon, EvalType.SELF),
            Eval(employees.jhon, employees.jane, EvalType.MY_SUPERVISOR),
            Eval(employees.jhon, employees.minion_1, EvalType.MY_MINION),
            Eval(employees.jhon, employees.minion_2, EvalType.MY_MINION),
            Eval(employees.jhon, employees.minion_3, EvalType.MY_MINION),
            Eval(employees.minion_1, employees.minion_1, EvalType.SELF),
            Eval(employees.minion_1, employees.jhon, EvalType.MY_SUPERVISOR),
            Eval(employees.minion_2, employees.minion_2, EvalType.SELF),
            Eval(employees.minion_2, employees.jhon, EvalType.MY_SUPERVISOR),
            Eval(employees.minion_3, employees.minion_3, EvalType.SELF),
            Eval(employees.minion_3, employees.jhon, EvalType.MY_SUPERVISOR),
        ])

    def test_create_initial_180_eval_suite_considering_peers(self):
        initial_eval_suite = self.org_chart_adapter.create_initial_eval_suite(
            self.org_chart, consider_peers=True)

        self.assertListEqual(initial_eval_suite.evals, [
            Eval(employees.jane, employees.jane, EvalType.SELF),
            Eval(employees.jane, employees.jhon, EvalType.MY_MINION),
            Eval(employees.jhon, employees.jhon, EvalType.SELF),
            Eval(employees.jhon, employees.jane, EvalType.MY_SUPERVISOR),
            Eval(employees.jhon, employees.minion_1, EvalType.MY_MINION),
            Eval(employees.jhon, employees.minion_2, EvalType.MY_MINION),
            Eval(employees.jhon, employees.minion_3, EvalType.MY_MINION),
            Eval(employees.minion_1, employees.minion_1, EvalType.SELF),
            Eval(employees.minion_1, employees.jhon, EvalType.MY_SUPERVISOR),
            Eval(employees.minion_1, employees.minion_2, EvalType.PEER),
            Eval(employees.minion_1, employees.minion_3, EvalType.PEER),
            Eval(employees.minion_2, employees.minion_2, EvalType.SELF),
            Eval(employees.minion_2, employees.jhon, EvalType.MY_SUPERVISOR),
            Eval(employees.minion_2, employees.minion_1, EvalType.PEER),
            Eval(employees.minion_2, employees.minion_3, EvalType.PEER),
            Eval(employees.minion_3, employees.minion_3, EvalType.SELF),
            Eval(employees.minion_3, employees.jhon, EvalType.MY_SUPERVISOR),
            Eval(employees.minion_3, employees.minion_1, EvalType.PEER),
            Eval(employees.minion_3, employees.minion_2, EvalType.PEER),
        ])

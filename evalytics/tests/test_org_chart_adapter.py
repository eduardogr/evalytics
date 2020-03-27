from unittest import TestCase

from evalytics.server.adapters import OrgChartAdapter
from evalytics.server.models import Eval, EvalType, OrgChart
from evalytics.tests.fixtures.employees import employee_nodes


class TestOrgChartAdapter(TestCase):

    def setUp(self):
        self.org_chart = OrgChart(employee_nodes().get('jane'))
        self.org_chart_adapter = OrgChartAdapter()  # subject

    def test_create_initial_180_eval_suite(self):
        initial_eval_suite = self.org_chart_adapter.create_initial_eval_suite(
            self.org_chart)

        self.assertListEqual(initial_eval_suite.evals, [
            Eval(employee_nodes().get('jane'), employee_nodes().get('jane'), EvalType.SELF),
            Eval(employee_nodes().get('jane'), employee_nodes().get('jhon'), EvalType.MY_MINION),
            Eval(employee_nodes().get('jhon'), employee_nodes().get('jhon'), EvalType.SELF),
            Eval(employee_nodes().get('jhon'), employee_nodes().get('jane'), EvalType.MY_SUPERVISOR),
            Eval(employee_nodes().get('jhon'), employee_nodes().get('minion_1'), EvalType.MY_MINION),
            Eval(employee_nodes().get('jhon'), employee_nodes().get('minion_2'), EvalType.MY_MINION),
            Eval(employee_nodes().get('jhon'), employee_nodes().get('minion_3'), EvalType.MY_MINION),
            Eval(employee_nodes().get('minion_1'), employee_nodes().get('minion_1'), EvalType.SELF),
            Eval(employee_nodes().get('minion_1'), employee_nodes().get('jhon'), EvalType.MY_SUPERVISOR),
            Eval(employee_nodes().get('minion_2'), employee_nodes().get('minion_2'), EvalType.SELF),
            Eval(employee_nodes().get('minion_2'), employee_nodes().get('jhon'), EvalType.MY_SUPERVISOR),
            Eval(employee_nodes().get('minion_3'), employee_nodes().get('minion_3'), EvalType.SELF),
            Eval(employee_nodes().get('minion_3'), employee_nodes().get('jhon'), EvalType.MY_SUPERVISOR),
        ])

    def test_create_initial_180_eval_suite_considering_peers(self):
        initial_eval_suite = self.org_chart_adapter.create_initial_eval_suite(
            self.org_chart, consider_peers=True)

        self.assertListEqual(initial_eval_suite.evals, [
            Eval(employee_nodes().get('jane'), employee_nodes().get('jane'), EvalType.SELF),
            Eval(employee_nodes().get('jane'), employee_nodes().get('jhon'), EvalType.MY_MINION),
            Eval(employee_nodes().get('jhon'), employee_nodes().get('jhon'), EvalType.SELF),
            Eval(employee_nodes().get('jhon'), employee_nodes().get('jane'), EvalType.MY_SUPERVISOR),
            Eval(employee_nodes().get('jhon'), employee_nodes().get('minion_1'), EvalType.MY_MINION),
            Eval(employee_nodes().get('jhon'), employee_nodes().get('minion_2'), EvalType.MY_MINION),
            Eval(employee_nodes().get('jhon'), employee_nodes().get('minion_3'), EvalType.MY_MINION),
            Eval(employee_nodes().get('minion_1'), employee_nodes().get('minion_1'), EvalType.SELF),
            Eval(employee_nodes().get('minion_1'), employee_nodes().get('jhon'), EvalType.MY_SUPERVISOR),
            Eval(employee_nodes().get('minion_1'), employee_nodes().get('minion_2'), EvalType.PEER),
            Eval(employee_nodes().get('minion_1'), employee_nodes().get('minion_3'), EvalType.PEER),
            Eval(employee_nodes().get('minion_2'), employee_nodes().get('minion_2'), EvalType.SELF),
            Eval(employee_nodes().get('minion_2'), employee_nodes().get('jhon'), EvalType.MY_SUPERVISOR),
            Eval(employee_nodes().get('minion_2'), employee_nodes().get('minion_1'), EvalType.PEER),
            Eval(employee_nodes().get('minion_2'), employee_nodes().get('minion_3'), EvalType.PEER),
            Eval(employee_nodes().get('minion_3'), employee_nodes().get('minion_3'), EvalType.SELF),
            Eval(employee_nodes().get('minion_3'), employee_nodes().get('jhon'), EvalType.MY_SUPERVISOR),
            Eval(employee_nodes().get('minion_3'), employee_nodes().get('minion_1'), EvalType.PEER),
            Eval(employee_nodes().get('minion_3'), employee_nodes().get('minion_2'), EvalType.PEER),
        ])

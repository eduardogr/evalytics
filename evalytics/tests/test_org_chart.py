from unittest import TestCase

from ..server.models import Employee, Eval, EvalType, OrgChart

# fixtures
jane = Employee('jane@tuenti.com')
jhon = Employee('jhon@tuenti.com', supervisor=jane)
minion_1 = Employee('minion1@tuenti.com', supervisor=jhon)
minion_2 = Employee('minion2@tuenti.com', supervisor=jhon)
minion_3 = Employee('minion3@tuenti.com', supervisor=jhon)


class TestOrgChart(TestCase):

    def setUp(self):
        self.org_chart = OrgChart(jane)  # subject

    def test_org_chart_keeps_the_expected_structure(self):
        minions_names = [
            minion.name for minion in self.org_chart.root.minions[0].minions
        ]
        self.assertListEqual(minions_names, ['minion1', 'minion2', 'minion3'])

    def test_org_chart_may_be_iterated(self):
        for employee in self.org_chart:
            self.assertIsInstance(employee, Employee)

    def test_org_chart_creates_an_eval_suite(self):
        eval_suite = self.org_chart.create_eval_suite()
        self.assertListEqual(eval_suite.initial_evals, [
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

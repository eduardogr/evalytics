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

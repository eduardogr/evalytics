from unittest import TestCase

from evalytics.server.models import OrgChart, Employee
from evalytics.tests.fixtures import employees


class TestOrgChart(TestCase):

    def setUp(self):
        self.org_chart = OrgChart(employees.jane)  # subject

    def test_org_chart_keeps_the_expected_structure(self):
        minions_names = [
            minion.name for minion in self.org_chart.root.minions[0].minions
        ]
        self.assertListEqual(minions_names, ['minion1', 'minion2', 'minion3'])

    def test_org_chart_may_be_iterated(self):
        for employee in self.org_chart:
            self.assertIsInstance(employee, Employee)

from unittest import TestCase

from evalytics.server.models import OrgChart, EmployeeNode
from evalytics.tests.fixtures.employees import employee_nodes


class TestOrgChart(TestCase):

    def setUp(self):
        self.org_chart = OrgChart(root=employee_nodes().get('jane'))

    def test_org_chart_keeps_the_expected_structure(self):
        minions_names = [
            minion.employee.uid for minion in self.org_chart.root.minions[0].minions
        ]
        self.assertListEqual(minions_names, ['minion1', 'minion2', 'minion3'])

    def test_org_chart_may_be_iterated(self):
        for employee_node in self.org_chart:
            self.assertIsInstance(employee_node, EmployeeNode)

from unittest import TestCase

from evalytics.server.adapters import EmployeeAdapter
from evalytics.server.config import Config
from evalytics.server.models import Employee, EvalKind, Eval, Reviewer
from evalytics.server.exceptions import MissingDataException

class MockConfig(Config):

    def __init__(self):
        super().__init__()
        self.needed_spreadsheets = []

    def read_google_folder(self):
        return "google_folder"

    def read_google_orgchart(self):
        return "google_orgchart"

    def read_google_form_map(self):
        return "google_form_map"

    def read_needed_spreadsheets(self):
        return self.needed_spreadsheets
    
    def read_company_domain(self):
        return "company.com"

    def read_company_number_of_employees(self):
        return 1000

    def set_needed_spreadhseets(self, needed_spreadhseets):
        self.needed_spreadsheets = needed_spreadhseets
class EmployeeAdapterSut(EmployeeAdapter, MockConfig):
    'Inject mocks into EmployeeAdapter dependencies'

class TestEmployeeAdapter(TestCase):

    def setUp(self):
        self.SELF_FORM = 'self form'
        self.PEER_MANAGER_FORM = 'peer manager form'
        self.MANAGER_PEER_FORM = 'manager peer form'
        self.AREA = 'eng'
        self.employees = {
            'ceo': Employee(
                mail='ceo@company.com', manager='', area=self.AREA),
            'cto': Employee(
                mail='cto@company.com', manager='ceo', area=self.AREA),
            'tl1': Employee(
                mail='tl1@company.com', manager='cto', area=self.AREA),
            'tl2': Employee(
                mail='tl2@company.com', manager='cto', area=self.AREA),
            'sw1': Employee(
                mail='sw1@company.com', manager='tl1', area=self.AREA),
            'sw2': Employee(
                mail='sw2@company.com', manager='tl1', area=self.AREA),
            'sw3': Employee(
                mail='sw3@company.com', manager='tl2', area=self.AREA),
            'sw4': Employee(
                mail='sw4@company.com', manager='tl2', area=self.AREA),
            'sw5': Employee(
                mail='sw5@company.com', manager='tl2', area=self.AREA),
        }
        self.employees_with_blacklisted_reviewers = {
            'cto': Employee(
                mail='cto@company.com', manager='ceo', area=self.AREA),
            'cto2': Employee(
                mail='cto2@company.com', manager='ceo', area=self.AREA),
            'tl1': Employee(
                mail='tl1@company.com', manager='cto', area=self.AREA),
            'sw1': Employee(
                mail='sw1@company.com', manager='tl1', area=self.AREA),
            'sw2': Employee(
                mail='sw2@company.com', manager='tl1', area=self.AREA),
        }
        self.forms = {
            self.AREA: {
                EvalKind.SELF: self.SELF_FORM,
                EvalKind.PEER_MANAGER: self.PEER_MANAGER_FORM,
                EvalKind.MANAGER_PEER: self.MANAGER_PEER_FORM,
            }
        }
        self.forms_with_other_area = {
            'NO_AREA': {
                EvalKind.SELF: self.SELF_FORM,
                EvalKind.PEER_MANAGER: self.PEER_MANAGER_FORM,
                EvalKind.MANAGER_PEER: self.MANAGER_PEER_FORM,
            }
        }

    def test_employee_adapter_get_managers(self):
        adapter = EmployeeAdapterSut()
        managers = adapter.get_employees_by_manager(self.employees)

        self.assertEqual(managers['ceo'], ['cto'])
        self.assertEqual(managers['cto'], ['tl1', 'tl2'])
        self.assertEqual(managers['tl1'], ['sw1', 'sw2'])
        self.assertEqual(managers['tl2'], ['sw3', 'sw4', 'sw5'])

    def test_employee_adapter_get_manager_when_uncompleted_employees(self):
        adapter = EmployeeAdapterSut()
        employees_by_manager = adapter.get_employees_by_manager(self.employees_with_blacklisted_reviewers)

        self.assertNotIn('ceo', employees_by_manager)
        self.assertEqual(employees_by_manager['cto'], ['tl1'])
        self.assertEqual(employees_by_manager['tl1'], ['sw1', 'sw2'])


    def test_employee_adapter_build_reviewers_correct_number_of_evals(self):
        adapter = EmployeeAdapterSut()
        reviewers = adapter.build_reviewers(self.employees, self.forms)

        self.assertIn('ceo', reviewers)
        self.assertIn('cto', reviewers)
        self.assertIn('tl1', reviewers)
        self.assertIn('tl2', reviewers)
        self.assertIn('sw1', reviewers)
        self.assertIn('sw2', reviewers)
        self.assertIn('sw3', reviewers)
        self.assertIn('sw4', reviewers)
        self.assertIn('sw5', reviewers)
        self.assertEqual(2, len(reviewers['ceo'].evals))
        self.assertEqual(4, len(reviewers['cto'].evals))
        self.assertEqual(4, len(reviewers['tl1'].evals))
        self.assertEqual(5, len(reviewers['tl2'].evals))
        self.assertEqual(2, len(reviewers['sw1'].evals))
        self.assertEqual(2, len(reviewers['sw2'].evals))
        self.assertEqual(2, len(reviewers['sw3'].evals))
        self.assertEqual(2, len(reviewers['sw4'].evals))
        self.assertEqual(2, len(reviewers['sw5'].evals))

    def test_employee_adapter_build_reviewers_correct_if_not_an_employee_and_is_manager(self):
        adapter = EmployeeAdapterSut()
        reviewers = adapter.build_reviewers(self.employees_with_blacklisted_reviewers, self.forms)

        self.assertIn('ceo', reviewers)
        self.assertEqual(2, len(reviewers['ceo'].evals))

    def test_employee_adapter_build_reviewers_correct_number_of_evals_when_uncompleted_employees(self):
        adapter = EmployeeAdapterSut()
        reviewers = adapter.build_reviewers(
            self.employees_with_blacklisted_reviewers,
            self.forms)

        self.assertIn('ceo', reviewers)
        self.assertIn('cto', reviewers)
        self.assertIn('cto2', reviewers)
        self.assertIn('tl1', reviewers)
        self.assertIn('sw1', reviewers)
        self.assertIn('sw2', reviewers)
        self.assertEqual(2, len(reviewers['ceo'].evals))
        self.assertEqual(3, len(reviewers['cto'].evals))
        self.assertEqual(4, len(reviewers['tl1'].evals))
        self.assertEqual(2, len(reviewers['sw1'].evals))
        self.assertEqual(2, len(reviewers['sw2'].evals))

    def test_employee_adapter_build_reviewers_correct_evals(self):
        adapter = EmployeeAdapterSut()
        reviewers = adapter.build_reviewers(self.employees, self.forms)

        self.assertEqual(reviewers['ceo'].evals, [
            Eval(reviewee='ceo',
                 kind=EvalKind.SELF, form=self.SELF_FORM),
            Eval(reviewee='cto', kind=EvalKind.MANAGER_PEER, form=self.MANAGER_PEER_FORM),
        ])

        self.assertEqual(reviewers['cto'].evals, [
             Eval(reviewee='cto',
                 kind=EvalKind.SELF, form=self.SELF_FORM),
            Eval(reviewee='ceo',
                 kind=EvalKind.PEER_MANAGER, form=self.PEER_MANAGER_FORM),
            Eval(reviewee='tl1',
                 kind=EvalKind.MANAGER_PEER, form=self.MANAGER_PEER_FORM),
            Eval(reviewee='tl2',
                 kind=EvalKind.MANAGER_PEER, form=self.MANAGER_PEER_FORM),
        ])

        self.assertEqual(reviewers['tl1'].evals, [
            Eval(reviewee='tl1',
                 kind=EvalKind.SELF, form=self.SELF_FORM),
            Eval(reviewee='cto',
                 kind=EvalKind.PEER_MANAGER, form=self.PEER_MANAGER_FORM),
            Eval(reviewee='sw1',
                 kind=EvalKind.MANAGER_PEER, form=self.MANAGER_PEER_FORM),
            Eval(reviewee='sw2',
                 kind=EvalKind.MANAGER_PEER, form=self.MANAGER_PEER_FORM),
        ])

        self.assertEqual(reviewers['tl2'].evals, [
            Eval(reviewee='tl2',
                 kind=EvalKind.SELF, form=self.SELF_FORM),
            Eval(reviewee='cto',
                 kind=EvalKind.PEER_MANAGER, form=self.PEER_MANAGER_FORM),
            Eval(reviewee='sw3',
                 kind=EvalKind.MANAGER_PEER, form=self.MANAGER_PEER_FORM),
            Eval(reviewee='sw4',
                 kind=EvalKind.MANAGER_PEER, form=self.MANAGER_PEER_FORM),
            Eval(reviewee='sw5',
                 kind=EvalKind.MANAGER_PEER, form=self.MANAGER_PEER_FORM),
        ])

    def test_test_employee_adapter_build_reviewers_with_no_forms(self):
        no_forms = {}
        adapter = EmployeeAdapterSut()

        with self.assertRaises(MissingDataException):
            adapter.build_reviewers(self.employees, no_forms)

    def test_test_employee_adapter_build_reviewers_with_other_area_forms(self):
        form_with_other_area = self.forms_with_other_area
        adapter = EmployeeAdapterSut()

        with self.assertRaises(MissingDataException):
            adapter.build_reviewers(self.employees, form_with_other_area)

    def test_employee_adapter_build_eval_message_correct(self):
        employee = self.employees['cto']
        reviewer = Reviewer(
            employee=employee,
            evals=[
                Eval(reviewee=employee.uid, kind=EvalKind.SELF, form="coolform"),
                Eval(reviewee='another', kind=EvalKind.MANAGER_PEER, form="coolformformanagers"),
            ]
        )

        adapter = EmployeeAdapterSut()
        eval_message = adapter.build_eval_message(reviewer)

        self.assertIn(employee.uid, eval_message)

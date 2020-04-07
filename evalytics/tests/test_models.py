from unittest import TestCase

from evalytics.server.models import Employee, Eval, EvalKind

class TestModels(TestCase):

    def test_employee_are_equals_by_uid(self):
        employee = Employee(
            mail='some@employee.com',
            manager='manager',
            area='Area'
        )
        other_employee = Employee(
            mail='some@employee.com',
            manager='',
            area=''
        )

        self.assertEqual(employee, other_employee)
    
    def test_employee_are_not_equals_by_uid(self):
        employee = Employee(
            mail='some@employee.com',
            manager='manager',
            area='Area'
        )
        other_employee = Employee(
            mail='simeome@employee.com',
            manager='manager',
            area='Area'
        )

        self.assertNotEqual(employee, other_employee)

    
    def test_eval_are_equals_by_all_fields(self):
        evaluation = Eval(
            reviewee='employee_uid',
            kind=EvalKind.SELF,
            form='my form'
        )
        other_evaluation = Eval(
            reviewee='employee_uid',
            kind=EvalKind.SELF,
            form='my form'
        )

        self.assertEqual(evaluation, other_evaluation)

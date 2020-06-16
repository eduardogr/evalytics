from unittest import TestCase

from evalytics.models import Employee, Eval, EvalKind, Reviewer
from evalytics.models import ReviewerResponseBuilder

class TestEval(TestCase):

    def setUp(self):
        self.evaluation = Eval(
            reviewee='employee_uid',
            kind=EvalKind.SELF,
            form='my form'
        )

    def test_eval_are_equals_by_all_fields(self):
        other_evaluation = Eval(
            reviewee='employee_uid',
            kind=EvalKind.SELF,
            form='my form'
        )

        self.assertEqual(self.evaluation, other_evaluation)

    def test_eval_to_json(self):
        jsondict = self.evaluation.to_json()

        self.assertEqual('employee_uid', jsondict['reviewee'])
        self.assertEqual(EvalKind.SELF.name, jsondict['kind'])
        self.assertEqual('my form', jsondict['form'])
        self.assertEqual(3, len(jsondict))

class TestEvalKind(TestCase):

    def test_evalkinf_from_str_self(self):
        eval_kind = EvalKind.SELF

        obtained_eval_kind = EvalKind.from_str(eval_kind.name)
        self.assertEqual(eval_kind, obtained_eval_kind)

    def test_evalkinf_from_str_peer(self):
        eval_kind = EvalKind.PEER_TO_PEER

        obtained_eval_kind = EvalKind.from_str(eval_kind.name)
        self.assertEqual(eval_kind, obtained_eval_kind)

    def test_evalkinf_from_str_peer_manager(self):
        eval_kind = EvalKind.PEER_MANAGER

        obtained_eval_kind = EvalKind.from_str(eval_kind.name)
        self.assertEqual(eval_kind, obtained_eval_kind)

    def test_evalkinf_from_str_manager_peer(self):
        eval_kind = EvalKind.MANAGER_PEER

        obtained_eval_kind = EvalKind.from_str(eval_kind.name)
        self.assertEqual(eval_kind, obtained_eval_kind)

    def test_evalkinf_from_str_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            EvalKind.from_str('NOT_EXISTING_EVAL_KIND')

class TestEmployee(TestCase):

    def setUp(self):
        self.employee = Employee(
            mail='some@employee.com',
            manager='manager',
            area='Area'
        )

    def test_employee_uid(self):
        self.assertEqual('some', self.employee.uid)

    def test_employee_when_has_no_manager(self):
        employee = Employee(
            mail='some@employee.com',
            manager='',
            area='Area'
        )

        self.assertFalse(employee.has_manager)

    def test_employee_when_has_manager(self):
        self.assertTrue(self.employee.has_manager)

    def test_employee_set_manager(self):
        employee = Employee(
            mail='some@employee.com',
            manager='',
            area='Area'
        )
        employee.manager = 'will'

        self.assertEqual('will', employee.manager)

    def test_employee_to_json(self):
        jsondict = self.employee.to_json()

        self.assertEqual('some', jsondict['uid'])
        self.assertEqual('some@employee.com', jsondict['mail'])
        self.assertEqual('manager', jsondict['manager'])
        self.assertEqual('Area', jsondict['area'])
        self.assertEqual(4, len(jsondict))
    
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

class TestReviewer(TestCase):

    def test_reviewer_uid(self):
        employee = Employee(
            mail='some@employee.com',
            manager='manager',
            area='Area'
        )
        reviewer = Reviewer(
            employee=employee,
            evals=[]
        )

        self.assertEqual('some', reviewer.uid)

    def test_reviewer_mail(self):
        employee = Employee(
            mail='some@employee.com',
            manager='manager',
            area='Area'
        )
        reviewer = Reviewer(
            employee=employee,
            evals=[]
        )

        self.assertEqual('some@employee.com', reviewer.mail)

    def test_reviewer_add_eval(self):
        employee = Employee(
            mail='some@employee.com',
            manager='manager',
            area='Area'
        )
        reviewer = Reviewer(
            employee=employee,
            evals=[]
        )
        reviewer.evals.append(Eval(
            reviewee='peer',
            kind=EvalKind.MANAGER_PEER,
            form='form'
        ))

        self.assertEqual(1, len(reviewer.evals))

    def test_reviewer_to_json(self):
        employee = Employee(
            mail='some@employee.com',
            manager='manager',
            area='Area'
        )
        reviewer = Reviewer(
            employee=employee,
            evals=[]
        )

        jsondict = reviewer.to_json()

        self.assertEqual('some@employee.com', jsondict['employee']['mail'])
        self.assertEqual([], jsondict['evals'])

    def test_reviewer_str(self):
        employee = Employee(
            mail='some@employee.com',
            manager='manager',
            area='Area'
        )
        reviewer = Reviewer(
            employee=employee,
            evals=[]
        )
        expected_str = "{'employee': {'mail': 'some@employee.com', 'uid': 'some', 'manager': 'manager', 'area': 'Area'}, 'evals': []}"

        reviewer_str = str(reviewer)

        self.assertEqual(expected_str, reviewer_str)

class TestReviewerResponseBuilder(TestCase):

    def setUp(self):
        self.questions = ['question1', 'question2']
        self.line_response = ['', 'manager1', 'reporter1', 'answer1', 'answer2']
        self.filename = 'this is a filename'
        self.eval_kind = 'super special eval kind'
        self.line_number = 169
        self.sut = ReviewerResponseBuilder()

    def test_build_correct_reviewer(self):
        # when:
        reviewer_response = self.sut.build(
            questions=self.questions,
            filename=self.filename,
            eval_kind=self.eval_kind,
            line=self.line_response,
            line_number=self.line_number
        )

        # then:
        self.assertEqual('manager1', reviewer_response.reviewer)

    def test_build_correct_reviewee(self):
        # when:
        reviewer_response = self.sut.build(
            questions=self.questions,
            filename=self.filename,
            eval_kind=self.eval_kind,
            line=self.line_response,
            line_number=self.line_number
        )

        # then:
        self.assertEqual('reporter1', reviewer_response.reviewee)

    def test_build_correct_eval_response(self):
        # when:
        reviewer_response = self.sut.build(
            questions=self.questions,
            filename=self.filename,
            eval_kind=self.eval_kind,
            line=self.line_response,
            line_number=self.line_number
        )

        # then:
        self.assertEqual(
            [('question1', 'answer1'), ('question2', 'answer2')],
            reviewer_response.eval_response
        )

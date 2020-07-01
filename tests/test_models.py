from unittest import TestCase

from evalytics.models import GoogleFile, GoogleSetup
from evalytics.models import Employee, Eval, EvalKind, Reviewer
from evalytics.models import ReviewerResponseBuilder
from evalytics.models import GoogleApiClientHttpError, PeersAssignment
from evalytics.models import CommunicationKind

class TestGoogleFile(TestCase):

    def setUp(self):
        self.any_name = 'name'
        self.any_id = 'ID'
        self.sut = GoogleFile(
            name=self.any_name,
            id=self.any_id
        )

    def test_ok_attributes(self):
        self.assertEqual(self.any_name, self.sut.name)
        self.assertEqual(self.any_id, self.sut.id)

    def test_to_json(self):
        expected_json = {
            'name': self.any_name,
            'id': self.any_id
        }
        self.assertEqual(expected_json, self.sut.to_json())

class TestGoogleSetup(TestCase):

    def setUp(self):
        self.any_name = 'name'
        self.any_id = 'ID'
        self.any_folder = GoogleFile(
            name=self.any_name,
            id=self.any_id
        )
        self.any_files = [self.any_folder, self.any_folder]
        self.sut = GoogleSetup(self.any_folder, self.any_files)

    def test_ok_attributes(self):
        self.assertEqual(self.any_folder, self.sut.folder)
        self.assertEqual(self.any_files, self.sut.files)

    def test_to_json(self):
        expected_json = {
            'folder': self.any_folder.to_json(),
            'files': [f.to_json() for f in self.any_files]
        }
        self.assertEqual(expected_json, self.sut.to_json())

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

    def test_eval_are_not_equals(self):
        other_evaluation = Eval(
            reviewee='OTHER',
            kind=EvalKind.SELF,
            form='my form'
        )

        self.assertFalse(self.evaluation == other_evaluation)

    def test_eval_are_not_equals_because_of_type(self):
        other_type = EvalKind.SELF

        self.assertFalse(self.evaluation == other_type)

    def test_eval_to_json(self):
        jsondict = self.evaluation.to_json()

        self.assertEqual('employee_uid', jsondict['reviewee'])
        self.assertEqual(EvalKind.SELF.name, jsondict['kind'])
        self.assertEqual('my form', jsondict['form'])
        self.assertEqual(3, len(jsondict))

class TestEvalKind(TestCase):

    def test_evalkind_from_str_self(self):
        eval_kind = EvalKind.SELF

        obtained_eval_kind = EvalKind.from_str(eval_kind.name)
        self.assertEqual(eval_kind, obtained_eval_kind)

    def test_evalkind_from_str_peer(self):
        eval_kind = EvalKind.PEER_TO_PEER

        obtained_eval_kind = EvalKind.from_str(eval_kind.name)
        self.assertEqual(eval_kind, obtained_eval_kind)

    def test_evalkind_from_str_peer_manager(self):
        eval_kind = EvalKind.PEER_MANAGER

        obtained_eval_kind = EvalKind.from_str(eval_kind.name)
        self.assertEqual(eval_kind, obtained_eval_kind)

    def test_evalkind_from_str_manager_peer(self):
        eval_kind = EvalKind.MANAGER_PEER

        obtained_eval_kind = EvalKind.from_str(eval_kind.name)
        self.assertEqual(eval_kind, obtained_eval_kind)

    def test_evalkind_from_str_peer_to_peer(self):
        eval_kind = EvalKind.PEER_TO_PEER

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

    def test_employee_are_not_equals_by_type(self):
        employee = Employee(
            mail='some@employee.com',
            manager='manager',
            area='Area'
        )
        other_type = EvalKind.SELF

        self.assertNotEqual(employee, other_type)

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

    def test_build_correct_reviewee_when_is_email(self):
        # given:
        line_response = ['', 'manager1', 'reporter1@company.com', 'answer1', 'answer2']

        # when:
        reviewer_response = self.sut.build(
            questions=self.questions,
            filename=self.filename,
            eval_kind=self.eval_kind,
            line=line_response,
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

class TestGoogleApiClientHttpError(TestCase):

    def setUp(self):
        self.code = 200
        self.message = "This is your friendly human-based text message"
        self.status = 201
        self.details = []

    def test_build_correct_google_api_client_http_error(self):
        # when:
        sut = GoogleApiClientHttpError(
            self.code,
            self.message,
            self.status,
            self.details,
        )

        # then:
        self.assertEqual(self.code, sut.code)
        self.assertEqual(self.message, sut.message)
        self.assertEqual(self.status, sut.status)
        self.assertEqual(self.details, sut.details)

    def test_to_json_google_api_client_http_error(self):
        # when:
        sut = GoogleApiClientHttpError(
            self.code,
            self.message,
            self.status,
            self.details,
        )
        json_http_error = sut.to_json()

        # then:
        self.assertIn("code", json_http_error)
        self.assertIn("message", json_http_error)
        self.assertIn("status", json_http_error)
        self.assertIn("details", json_http_error)

class TestCommunicationKind(TestCase):

    def test_communicationkind_from_str_peers_assignment(self):
        # given:
        communication_kind = CommunicationKind.PEERS_ASSIGNMENT
        communication_kind_str = 'peers_assignment'

        # when:
        obtained_communication_kind = CommunicationKind.from_str(communication_kind_str)

        # then:
        self.assertEqual(communication_kind, obtained_communication_kind)

    def test_communicationkind_from_str_process_started(self):
        # given:
        communication_kind = CommunicationKind.PROCESS_STARTED
        communication_kind_str = 'process_started'

        # when:
        obtained_communication_kind = CommunicationKind.from_str(communication_kind_str)

        # then:
        self.assertEqual(communication_kind, obtained_communication_kind)

    def test_communicationkind_from_str_due_date_reminder(self):
        # given:
        communication_kind = CommunicationKind.DUE_DATE_REMINDER
        communication_kind_str = 'due_date_reminder'

        # when:
        obtained_communication_kind = CommunicationKind.from_str(communication_kind_str)

        # then:
        self.assertEqual(communication_kind, obtained_communication_kind)

    def test_communicationkind_from_str_pending_evals_reminder(self):
        # given:
        communication_kind = CommunicationKind.PENDING_EVALS_REMINDER
        communication_kind_str = 'pending_evals_reminder'

        # when:
        obtained_communication_kind = CommunicationKind.from_str(communication_kind_str)

        # then:
        self.assertEqual(communication_kind, obtained_communication_kind)

    def test_communicationkind_from_str_process_finished(self):
        # given:
        communication_kind = CommunicationKind.PROCESS_FINISHED
        communication_kind_str = 'process_finished'

        # when:
        obtained_communication_kind = CommunicationKind.from_str(communication_kind_str)

        # then:
        self.assertEqual(communication_kind, obtained_communication_kind)

    def test_communicationkind_from_str_not_implemented(self):
        with self.assertRaises(ValueError):
            CommunicationKind.from_str('NOT_EXISTING_COMMUNICATION_KIND')

class TestPeersAssignment(TestCase):

    def setUp(self):
        self.any_peers = {'reviewer': ['peer1', 'peer2']}
        self.any_unanswered_forms = ['unanswered form 1']
        self.sut = PeersAssignment(self.any_peers, self.any_unanswered_forms)

    def test_ok_attributes(self):
        self.assertEqual(self.any_peers, self.sut.peers)
        self.assertEqual(self.any_unanswered_forms, self.sut.unanswered_forms)

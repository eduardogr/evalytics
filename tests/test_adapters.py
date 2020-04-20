from unittest import TestCase

from evalytics.adapters import EmployeeAdapter, ReviewerAdapter
from evalytics.models import Employee, EvalKind, Eval, Reviewer
from evalytics.exceptions import MissingDataException

from tests.common.mocks import MockConfig, MockEmployeeAdapter

class EmployeeAdapterSut(EmployeeAdapter, MockConfig):
    'Inject mocks into EmployeeAdapter dependencies'

class ReviewerAdapterSut(ReviewerAdapter, MockEmployeeAdapter):
    'Inject mocks into ReviewerAdapter dependencies'

class TestEmployeeAdapter(TestCase):

    def setUp(self):
        self.sut = EmployeeAdapterSut()
        self.self_form = 'self form'
        self.peer_manager_form = 'peer manager form'
        self.manager_peer_form = 'manager peer form'
        self.area = 'eng'
        self.employees = {
            'ceo': Employee(
                mail='ceo@company.com', manager='', area=self.area),
            'cto': Employee(
                mail='cto@company.com', manager='ceo', area=self.area),
            'tl1': Employee(
                mail='tl1@company.com', manager='cto', area=self.area),
            'tl2': Employee(
                mail='tl2@company.com', manager='cto', area=self.area),
            'sw1': Employee(
                mail='sw1@company.com', manager='tl1', area=self.area),
            'sw2': Employee(
                mail='sw2@company.com', manager='tl1', area=self.area),
            'sw3': Employee(
                mail='sw3@company.com', manager='tl2', area=self.area),
            'sw4': Employee(
                mail='sw4@company.com', manager='tl2', area=self.area),
            'sw5': Employee(
                mail='sw5@company.com', manager='tl2', area=self.area),
        }
        self.employees_with_blacklisted_reviewers = {
            'cto': Employee(
                mail='cto@company.com', manager='ceo', area=self.area),
            'cto2': Employee(
                mail='cto2@company.com', manager='ceo', area=self.area),
            'tl1': Employee(
                mail='tl1@company.com', manager='cto', area=self.area),
            'sw1': Employee(
                mail='sw1@company.com', manager='tl1', area=self.area),
            'sw2': Employee(
                mail='sw2@company.com', manager='tl1', area=self.area),
        }
        self.forms = {
            self.area: {
                EvalKind.SELF: self.self_form,
                EvalKind.PEER_MANAGER: self.peer_manager_form,
                EvalKind.MANAGER_PEER: self.manager_peer_form,
            }
        }
        self.forms_with_other_area = {
            'NO_AREA': {
                EvalKind.SELF: self.self_form,
                EvalKind.PEER_MANAGER: self.peer_manager_form,
                EvalKind.MANAGER_PEER: self.manager_peer_form,
            }
        }

    def test_get_managers(self):
        managers = self.sut.get_employees_by_manager(self.employees)

        self.assertEqual(managers['ceo'], ['cto'])
        self.assertEqual(managers['cto'], ['tl1', 'tl2'])
        self.assertEqual(managers['tl1'], ['sw1', 'sw2'])
        self.assertEqual(managers['tl2'], ['sw3', 'sw4', 'sw5'])

    def test_get_manager_when_uncompleted_employees(self):
        employees_by_manager = self.sut.get_employees_by_manager(self.employees_with_blacklisted_reviewers)

        self.assertNotIn('ceo', employees_by_manager)
        self.assertEqual(employees_by_manager['cto'], ['tl1'])
        self.assertEqual(employees_by_manager['tl1'], ['sw1', 'sw2'])


    def test_build_reviewers_correct_number_of_evals(self):
        reviewers = self.sut.build_reviewers(self.employees, self.forms)

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

    def test_build_reviewers_correct_if_not_an_employee_and_is_manager(self):
        reviewers = self.sut.build_reviewers(
            self.employees_with_blacklisted_reviewers,
            self.forms)

        self.assertIn('ceo', reviewers)
        self.assertEqual(2, len(reviewers['ceo'].evals))

    def test_build_reviewers_correct_number_of_evals_when_uncompleted_employees(self):
        reviewers = self.sut.build_reviewers(
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

    def test_build_reviewers_correct_evals(self):
        reviewers = self.sut.build_reviewers(self.employees, self.forms)

        self.assertEqual(reviewers['ceo'].evals, [
            Eval(reviewee='ceo',
                 kind=EvalKind.SELF, form=self.self_form),
            Eval(reviewee='cto', kind=EvalKind.MANAGER_PEER, form=self.manager_peer_form),
        ])

        self.assertEqual(reviewers['cto'].evals, [
             Eval(reviewee='cto',
                 kind=EvalKind.SELF, form=self.self_form),
            Eval(reviewee='ceo',
                 kind=EvalKind.PEER_MANAGER, form=self.peer_manager_form),
            Eval(reviewee='tl1',
                 kind=EvalKind.MANAGER_PEER, form=self.manager_peer_form),
            Eval(reviewee='tl2',
                 kind=EvalKind.MANAGER_PEER, form=self.manager_peer_form),
        ])

        self.assertEqual(reviewers['tl1'].evals, [
            Eval(reviewee='tl1',
                 kind=EvalKind.SELF, form=self.self_form),
            Eval(reviewee='cto',
                 kind=EvalKind.PEER_MANAGER, form=self.peer_manager_form),
            Eval(reviewee='sw1',
                 kind=EvalKind.MANAGER_PEER, form=self.manager_peer_form),
            Eval(reviewee='sw2',
                 kind=EvalKind.MANAGER_PEER, form=self.manager_peer_form),
        ])

        self.assertEqual(reviewers['tl2'].evals, [
            Eval(reviewee='tl2',
                 kind=EvalKind.SELF, form=self.self_form),
            Eval(reviewee='cto',
                 kind=EvalKind.PEER_MANAGER, form=self.peer_manager_form),
            Eval(reviewee='sw3',
                 kind=EvalKind.MANAGER_PEER, form=self.manager_peer_form),
            Eval(reviewee='sw4',
                 kind=EvalKind.MANAGER_PEER, form=self.manager_peer_form),
            Eval(reviewee='sw5',
                 kind=EvalKind.MANAGER_PEER, form=self.manager_peer_form),
        ])

    def test_build_reviewers_with_no_forms(self):
        no_forms = {}

        with self.assertRaises(MissingDataException):
            self.sut.build_reviewers(self.employees, no_forms)

    def test_build_reviewers_with_other_area_forms(self):
        form_with_other_area = self.forms_with_other_area

        with self.assertRaises(MissingDataException):
            self.sut.build_reviewers(self.employees, form_with_other_area)

    def test_build_eval_message_correct(self):
        employee = self.employees['cto']
        reviewer = Reviewer(
            employee=employee,
            evals=[
                Eval(reviewee=employee.uid, kind=EvalKind.SELF, form="coolform"),
                Eval(reviewee='another', kind=EvalKind.MANAGER_PEER, form="coolformformanagers"),
            ]
        )

        eval_message = self.sut.build_eval_message(reviewer)

        self.assertIn(employee.uid, eval_message)

class TestReviewerAdapter(TestCase):

    def setUp(self):
        self.sut = ReviewerAdapterSut()

        self.area = 'Eng'
        self.any_form = 'https://i am a form and you trust me'
        self.employees = {
            'cto': Employee(
                mail='cto@company.com', manager='ceo', area=self.area),
            'tl1': Employee(
                mail='tl1@company.com', manager='cto', area=self.area),
            'tl2': Employee(
                mail='tl2@company.com', manager='cto', area=self.area),
            'sw1': Employee(
                mail='sw1@company.com', manager='tl1', area=self.area),
            'sw2': Employee(
                mail='sw2@company.com', manager='tl1', area=self.area),
            'sw3': Employee(
                mail='sw3@company.com', manager='tl2', area=self.area),
        }
        self.employees_by_manager = {
            'cto': ['tl1', 'tl2'],
            'tl1': ['sw1', 'sw2'],
            'tl2': ['sw3']
        }
        self.reviewers = {
            self.employees['cto'].uid: Reviewer(
                employee=self.employees['cto'],
                evals=[
                    Eval(reviewee='tl1', kind=EvalKind.MANAGER_PEER, form=self.any_form),
                    Eval(reviewee='tl2', kind=EvalKind.MANAGER_PEER, form=self.any_form),
                ]
            ),
            self.employees['tl1'].uid: Reviewer(
                employee=self.employees['tl1'],
                evals=[
                    Eval(reviewee='cto', kind=EvalKind.PEER_MANAGER, form=self.any_form),
                    Eval(reviewee='tl1', kind=EvalKind.SELF, form=self.any_form),
                    Eval(reviewee='sw1', kind=EvalKind.MANAGER_PEER, form=self.any_form),
                    Eval(reviewee='sw2', kind=EvalKind.MANAGER_PEER, form=self.any_form),
                ]
            ),
            self.employees['tl2'].uid: Reviewer(
                employee=self.employees['tl2'],
                evals=[
                    Eval(reviewee='cto', kind=EvalKind.PEER_MANAGER, form=self.any_form),
                    Eval(reviewee='tl2', kind=EvalKind.SELF, form=self.any_form),
                    Eval(reviewee='sw3', kind=EvalKind.MANAGER_PEER, form=self.any_form),
                ]
            ),
            self.employees['sw1'].uid: Reviewer(
                employee=self.employees['sw1'],
                evals=[
                    Eval(reviewee='sw1', kind=EvalKind.SELF, form=self.any_form),
                    Eval(reviewee='tl1', kind=EvalKind.PEER_MANAGER, form=self.any_form),
                ]
            ),
            self.employees['sw2'].uid: Reviewer(
                employee=self.employees['sw2'],
                evals=[
                    Eval(reviewee='sw2', kind=EvalKind.SELF, form=self.any_form),
                    Eval(reviewee='tl1', kind=EvalKind.PEER_MANAGER, form=self.any_form),
                ]
            ),
            self.employees['sw3'].uid: Reviewer(
                employee=self.employees['sw3'],
                evals=[
                    Eval(reviewee='sw3', kind=EvalKind.SELF, form=self.any_form),
                    Eval(reviewee='tl2', kind=EvalKind.PEER_MANAGER, form=self.any_form),
                ]
            ),
        }

    def test_get_status_from_responses_when_no_responses(self):
        reviewers = {}
        responses = {}
        self.sut.set_employees_by_manager({})

        completed, pending, inconsistent = self.sut.get_status_from_responses(
            reviewers,
            responses)

        self.assertEqual(0, len(completed))
        self.assertEqual(0, len(pending))
        self.assertEqual(0, len(inconsistent))

    def test_get_status_from_responses_when_pending_responses(self):
        self.sut.set_employees_by_manager(self.employees_by_manager)
        responses = {
            self.reviewers['cto'].uid: [],
            self.reviewers['tl1'].uid: [],
            self.reviewers['tl2'].uid: [],
            self.reviewers['sw3'].uid: [],
            self.reviewers['sw2'].uid: [],
            self.reviewers['sw3'].uid: [],
        }

        completed, pending, inconsistent = self.sut.get_status_from_responses(
            self.reviewers,
            responses)

        self.assertEqual(0, len(completed))
        self.assertEqual(6, len(pending))
        self.assertEqual(0, len(inconsistent))

        self.assertIn('cto', pending)
        self.assertIn('tl1', pending)
        self.assertIn('tl2', pending)
        self.assertIn('sw1', pending)
        self.assertIn('sw2', pending)
        self.assertIn('sw3', pending)

        self.assertIn('tl1', pending['cto'])
        self.assertIn('tl2', pending['cto'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, pending['cto']['tl1']['kind'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, pending['cto']['tl2']['kind'])

        self.assertIn('sw1', pending['tl1'])
        self.assertIn('sw2', pending['tl1'])
        self.assertIn('tl1', pending['tl1'])
        self.assertEqual(EvalKind.SELF.name, pending['tl1']['tl1']['kind'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, pending['tl1']['sw1']['kind'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, pending['tl1']['sw2']['kind'])

        self.assertIn('sw3', pending['tl2'])
        self.assertIn('tl2', pending['tl2'])
        self.assertEqual(EvalKind.SELF.name, pending['tl2']['tl2']['kind'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, pending['tl2']['sw3']['kind'])

    def test_get_status_from_responses_when_some_completed_responses(self):
        self.sut.set_employees_by_manager(self.employees_by_manager)
        responses = {
            self.reviewers['cto'].uid: [{
                    'kind': 'MANAGER_PEER',
                    'reviewee': 'tl1',
                    'eval_response': [],
                }, {
                    'kind': 'MANAGER_PEER',
                    'reviewee': 'tl2',
                    'eval_response': [],
                }
            ],
            self.reviewers['tl1'].uid: [],
            self.reviewers['tl2'].uid: [],
            self.reviewers['sw1'].uid: [],
            self.reviewers['sw2'].uid: [],
            self.reviewers['sw3'].uid: [],
        }

        completed, pending, inconsistent = self.sut.get_status_from_responses(
            self.reviewers,
            responses)

        self.assertEqual(0, len(inconsistent))
        self.assertEqual(5, len(pending))
        self.assertEqual(1, len(completed))

        self.assertIn('cto', completed)
        self.assertIn('tl1', completed['cto'])
        self.assertIn('tl2', completed['cto'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, completed['cto']['tl1']['kind'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, completed['cto']['tl2']['kind'])

        self.assertIn('tl1', pending)
        self.assertIn('tl2', pending)
        self.assertIn('sw1', pending)
        self.assertIn('sw2', pending)
        self.assertIn('sw3', pending)

    def test_get_status_from_responses_when_completed_responses(self):
        self.sut.set_employees_by_manager(self.employees_by_manager)
        responses = {
            self.reviewers['cto'].uid: [{
                    'kind': 'MANAGER_PEER',
                    'reviewee': 'tl1',
                    'eval_response': [],
                }, {
                    'kind': 'MANAGER_PEER',
                    'reviewee': 'tl2',
                    'eval_response': [],
                }
            ],
            self.reviewers['tl1'].uid: [{
                    'kind': 'MANAGER_PEER',
                    'reviewee': 'sw1',
                    'eval_response': [],
                }
            ],
            self.reviewers['tl2'].uid: [],
            self.reviewers['sw1'].uid: [],
            self.reviewers['sw2'].uid: [],
            self.reviewers['sw3'].uid: [],
        }

        completed, pending, inconsistent = self.sut.get_status_from_responses(
            self.reviewers,
            responses)

        self.assertEqual(0, len(inconsistent))
        self.assertEqual(5, len(pending))
        self.assertEqual(2, len(completed))

        self.assertIn('cto', completed)
        self.assertIn('tl1', completed)
        self.assertIn('tl1', completed['cto'])
        self.assertIn('tl2', completed['cto'])
        self.assertIn('sw1', completed['tl1'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, completed['cto']['tl1']['kind'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, completed['cto']['tl2']['kind'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, completed['tl1']['sw1']['kind'])

        self.assertIn('sw2', pending['tl1'])
        self.assertIn('tl1', pending['tl1'])
        self.assertEqual(EvalKind.SELF.name, pending['tl1']['tl1']['kind'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, pending['tl1']['sw2']['kind'])


    def test_get_status_from_responses_when_inconsistent_reporter_responses(self):
        self.sut.set_employees_by_manager(self.employees_by_manager)
        responses = {
            self.reviewers['cto'].uid: [{
                    'kind': 'MANAGER_PEER',
                    'reviewee': 'tl1',
                    'eval_response': [],
                }, {
                    'kind': 'MANAGER_PEER',
                    'reviewee': 'tl2',
                    'eval_response': [],
                }
            ],
            self.reviewers['tl1'].uid: [{
                    'kind': 'MANAGER_PEER',
                    'reviewee': 'sw1',
                    'eval_response': [],
                }, {
                    'kind': 'MANAGER_PEER',
                    'reviewee': 'sw3',
                    'eval_response': [],
                }
            ],
            self.reviewers['tl2'].uid: [],
            self.reviewers['sw1'].uid: [],
            self.reviewers['sw2'].uid: [],
            self.reviewers['sw3'].uid: [],
        }

        completed, pending, inconsistent = self.sut.get_status_from_responses(
            self.reviewers,
            responses)

        self.assertEqual(1, len(inconsistent))
        self.assertEqual(5, len(pending))
        self.assertEqual(2, len(completed))

        self.assertIn('cto', completed)
        self.assertIn('tl1', completed)
        self.assertIn('tl1', completed['cto'])
        self.assertIn('tl2', completed['cto'])
        self.assertIn('sw1', completed['tl1'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, completed['cto']['tl1']['kind'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, completed['cto']['tl2']['kind'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, completed['tl1']['sw1']['kind'])

        self.assertIn('tl1', inconsistent)
        self.assertIn('sw3', inconsistent['tl1'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, inconsistent['tl1']['sw3']['kind'])

        self.assertTrue(inconsistent['tl1']['sw3']['reason'].startswith('WRONG_REPORTER'))

    def test_get_status_from_responses_when_inconsistent_manager_responses(self):
        self.sut.set_employees_by_manager(self.employees_by_manager)
        responses = {
            self.reviewers['cto'].uid: [{
                    'kind': 'MANAGER_PEER',
                    'reviewee': 'tl1',
                    'eval_response': [],
                }, {
                    'kind': 'MANAGER_PEER',
                    'reviewee': 'tl2',
                    'eval_response': [],
                }
            ],
            self.reviewers['tl1'].uid: [{
                    'kind': 'MANAGER_PEER',
                    'reviewee': 'sw1',
                    'eval_response': [],
                }, {
                    'kind': 'MANAGER_PEER',
                    'reviewee': 'sw2',
                    'eval_response': [],
                }
            ],
            self.reviewers['tl2'].uid: [],
            self.reviewers['sw1'].uid: [{
                    'kind': 'PEER_MANAGER',
                    'reviewee': 'tl2',
                    'eval_response': [],
            }],
            self.reviewers['sw2'].uid: [],
            self.reviewers['sw3'].uid: [],
        }

        completed, pending, inconsistent = self.sut.get_status_from_responses(
            self.reviewers,
            responses)

        self.assertEqual(1, len(inconsistent))
        self.assertEqual(5, len(pending))
        self.assertEqual(2, len(completed))

        self.assertIn('cto', completed)
        self.assertIn('tl1', completed)
        self.assertIn('tl1', completed['cto'])
        self.assertIn('tl2', completed['cto'])
        self.assertIn('sw1', completed['tl1'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, completed['cto']['tl1']['kind'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, completed['cto']['tl2']['kind'])
        self.assertEqual(EvalKind.MANAGER_PEER.name, completed['tl1']['sw1']['kind'])

        self.assertIn('sw1', inconsistent)
        self.assertIn('tl2', inconsistent['sw1'])
        self.assertEqual(EvalKind.PEER_MANAGER.name, inconsistent['sw1']['tl2']['kind'])

        self.assertTrue(inconsistent['sw1']['tl2']['reason'].startswith('WRONG_MANAGER'))

from unittest import TestCase

from evalytics.adapters import EmployeeAdapter, ReviewerAdapter
from evalytics.models import EvalKind, Eval
from evalytics.models import ReviewerResponse
from evalytics.exceptions import MissingDataException

from tests.common.mocks import MockConfig, MockEmployeeAdapter
from tests.common.fixture import Fixture

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
        self.peer_to_peer_form = 'peer to peer form'
        self.employees = Fixture().get_organization()
        cto = self.employees['cto']
        tl1 = self.employees['tl1']
        sw1 = self.employees['sw1']
        sw2 = self.employees['sw2']

        self.employees_with_blacklisted_reviewers = {
            'cto': cto,
            'cto2': Fixture().create_employee('cto2', 'ceo'),
            'tl1': tl1,
            'sw1': sw1,
            'sw2': sw2,
        }
        self.no_peers = {}
        self.peers = {
            'tl1': ['tl2', 'tl1', 'sw1', 'sw2'],
            'sw1': ['tl1', 'sw1', 'sw2', 'sw3', 'sw4', 'sw5'],
            'sw2': ['sw1', 'sw2', 'sw3', 'sw4'],
            'sw3': ['tl2', 'sw1', 'sw3'],
            'sw4': ['tl2', 'sw1'],
        }
        self.no_forms = {}
        self.forms = {
            cto.area: {
                EvalKind.SELF.name: self.self_form,
                EvalKind.PEER_MANAGER.name: self.peer_manager_form,
                EvalKind.MANAGER_PEER.name: self.manager_peer_form,
                EvalKind.PEER_TO_PEER.name: self.peer_to_peer_form,
            }
        }
        self.forms_with_other_area = {
            'NO_AREA': {}
        }

    def test_get_employee_manager_for_cto(self):
        # given:
        employee_uid = 'cto'

        # when:
        managers = self.sut.get_employee_managers(self.employees, employee_uid)

        # then:
        self.assertEqual(1, len(managers))
        self.assertIn('ceo', managers)

    def test_get_employee_manager_for_sw(self):
        # given:
        employee_uid = 'sw1'

        # when:
        managers = self.sut.get_employee_managers(self.employees, employee_uid)

        self.assertEqual(3, len(managers))
        self.assertIn('tl1', managers)
        self.assertIn('cto', managers)
        self.assertIn('ceo', managers)

    def test_get_managers(self):
        # when:
        managers = self.sut.get_employees_by_manager(self.employees)

        # then:
        self.assertEqual(managers['ceo'], ['cto'])
        self.assertEqual(managers['cto'], ['tl1', 'tl2'])
        self.assertEqual(managers['tl1'], ['sw1', 'sw2'])
        self.assertEqual(managers['tl2'], ['sw3', 'sw4', 'sw5'])

    def test_get_manager_when_uncompleted_employees(self):
        # when:
        employees_by_manager = self.sut.get_employees_by_manager(self.employees_with_blacklisted_reviewers)

        # then:
        self.assertNotIn('ceo', employees_by_manager)
        self.assertEqual(employees_by_manager['cto'], ['tl1'])
        self.assertEqual(employees_by_manager['tl1'], ['sw1', 'sw2'])

    def test_build_reviewers_correct_number_of_evals(self):
        # when:
        reviewers = self.sut.build_reviewers(self.employees, self.no_peers, self.forms)

        # then:
        self.__assert_all_employees_in(reviewers)
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
        # when:
        reviewers = self.sut.build_reviewers(
            self.employees_with_blacklisted_reviewers,
            self.no_peers,
            self.forms)

        # then:
        self.assertIn('ceo', reviewers)
        self.assertEqual(2, len(reviewers['ceo'].evals))

    def test_build_reviewers_correct_number_of_evals_when_uncompleted_employees(self):
        reviewers = self.sut.build_reviewers(
            self.employees_with_blacklisted_reviewers,
            self.no_peers,
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
        # when:
        reviewers = self.sut.build_reviewers(self.employees, self.no_peers, self.forms)

        # then:
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
        with self.assertRaises(MissingDataException):
            self.sut.build_reviewers(self.employees, self.no_peers, self.no_forms)

    def test_build_reviewers_with_other_area_forms(self):
        # given:
        form_with_other_area = self.forms_with_other_area

        # when:
        with self.assertRaises(MissingDataException):
            self.sut.build_reviewers(self.employees, self.no_peers, form_with_other_area)

    def test_build_reviewers_with_peers(self):
        # when:
        reviewers = self.sut.build_reviewers(self.employees, self.peers, self.forms)

        # then:
        self.__assert_all_employees_in(reviewers)
        self.assertEqual(2, len(reviewers['ceo'].evals))
        self.assertEqual(4, len(reviewers['cto'].evals))
        self.assertEqual(5, len(reviewers['tl1'].evals))
        self.assertEqual(5, len(reviewers['tl2'].evals))
        self.assertEqual(6, len(reviewers['sw1'].evals))
        self.assertEqual(5, len(reviewers['sw2'].evals))
        self.assertEqual(3, len(reviewers['sw3'].evals))
        self.assertEqual(3, len(reviewers['sw4'].evals))
        self.assertEqual(2, len(reviewers['sw5'].evals))

    def __assert_all_employees_in(self, reviewers):
        self.assertIn('ceo', reviewers)
        self.assertIn('cto', reviewers)
        self.assertIn('tl1', reviewers)
        self.assertIn('tl2', reviewers)
        self.assertIn('sw1', reviewers)
        self.assertIn('sw2', reviewers)
        self.assertIn('sw3', reviewers)
        self.assertIn('sw4', reviewers)
        self.assertIn('sw5', reviewers)

class TestReviewerAdapter(TestCase):

    def setUp(self):
        self.sut = ReviewerAdapterSut()
        self.employees_by_manager = Fixture().get_organization_employees_by_managers()
        self.reviewers = Fixture().get_organization_reviewers()

    def test_get_status_from_responses_when_no_responses(self):
        # given:
        reviewers = {}
        responses = {}
        self.sut.set_employees_by_manager({})

        # when:
        completed, pending, inconsistent = self.sut.get_status_from_responses(
            reviewers,
            responses)

        # then:
        self.assertEqual(0, len(completed))
        self.assertEqual(0, len(pending))
        self.assertEqual(0, len(inconsistent))

    def test_get_status_from_responses_when_pending_responses(self):
        # given:
        self.sut.set_employees_by_manager(self.employees_by_manager)
        responses = {
            self.reviewers['cto'].uid: [],
            self.reviewers['tl1'].uid: [],
            self.reviewers['tl2'].uid: [],
            self.reviewers['sw3'].uid: [],
            self.reviewers['sw2'].uid: [],
            self.reviewers['sw3'].uid: [],
        }

        # when:
        completed, pending, inconsistent = self.sut.get_status_from_responses(
            self.reviewers,
            responses)

        # then:
        self.assertEqual(0, len(completed))
        self.assertEqual(6, len(pending))
        self.assertEqual(0, len(inconsistent))

        self.assertIn('cto', pending)
        self.assertIn('tl1', pending)
        self.assertIn('tl2', pending)
        self.assertIn('sw1', pending)
        self.assertIn('sw2', pending)
        self.assertIn('sw3', pending)

        self.assertEqual(2, len(pending['cto'].evals))
        self.assertEqual(4, len(pending['tl1'].evals))
        self.assertEqual(3, len(pending['tl2'].evals))
        self.assertEqual(2, len(pending['sw1'].evals))
        self.assertEqual(2, len(pending['sw2'].evals))
        self.assertEqual(2, len(pending['sw3'].evals))

    def test_get_status_from_responses_when_some_completed_responses(self):
        # given:
        self.sut.set_employees_by_manager(self.employees_by_manager)
        responses = {
            self.reviewers['cto'].uid: [
                ReviewerResponse(
                    eval_kind=EvalKind.MANAGER_PEER,
                    reviewee='tl1',
                    reviewer='cto',
                    filename='',
                    line_number=0,
                    eval_response=[]),
                ReviewerResponse(
                    eval_kind=EvalKind.MANAGER_PEER,
                    reviewee='tl2',
                    reviewer='cto',
                    filename='',
                    line_number=0,
                    eval_response=[])
            ],
            self.reviewers['tl1'].uid: [],
            self.reviewers['tl2'].uid: [],
            self.reviewers['sw1'].uid: [],
            self.reviewers['sw2'].uid: [],
            self.reviewers['sw3'].uid: [],
        }

        # when:
        completed, pending, inconsistent = self.sut.get_status_from_responses(
            self.reviewers,
            responses)

        # then:
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
        # given:
        self.sut.set_employees_by_manager(self.employees_by_manager)
        responses = {
            self.reviewers['cto'].uid: [
                ReviewerResponse(
                    eval_kind=EvalKind.MANAGER_PEER,
                    reviewee='tl1',
                    reviewer='cto',
                    filename='',
                    line_number=0,
                    eval_response=[]),
                ReviewerResponse(
                    eval_kind=EvalKind.MANAGER_PEER,
                    reviewee='tl2',
                    reviewer='cto',
                    filename='',
                    line_number=0,
                    eval_response=[])
            ],
            self.reviewers['tl1'].uid: [
                ReviewerResponse(
                    eval_kind=EvalKind.MANAGER_PEER,
                    reviewee='sw1',
                    reviewer='tl1',
                    filename='',
                    line_number=0,
                    eval_response=[])
            ],
            self.reviewers['tl2'].uid: [],
            self.reviewers['sw1'].uid: [],
            self.reviewers['sw2'].uid: [],
            self.reviewers['sw3'].uid: [],
        }

        # when:
        completed, pending, inconsistent = self.sut.get_status_from_responses(
            self.reviewers,
            responses)

        # then:
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

        self.assertEqual(3, len(pending['tl1'].evals))


    def test_get_status_from_responses_when_inconsistent_reporter_responses(self):
        # given:
        self.sut.set_employees_by_manager(self.employees_by_manager)
        responses = {
            self.reviewers['cto'].uid: [
                ReviewerResponse(
                    eval_kind=EvalKind.MANAGER_PEER,
                    reviewee='tl1',
                    reviewer='cto',
                    filename='',
                    line_number=0,
                    eval_response=[]),
                ReviewerResponse(
                    eval_kind=EvalKind.MANAGER_PEER,
                    reviewee='tl2',
                    reviewer='cto',
                    filename='',
                    line_number=0,
                    eval_response=[])
            ],
            self.reviewers['tl1'].uid: [
                ReviewerResponse(
                    eval_kind=EvalKind.MANAGER_PEER,
                    reviewee='sw1',
                    reviewer='tl1',
                    filename='',
                    line_number=0,
                    eval_response=[]),
                ReviewerResponse(
                    eval_kind=EvalKind.MANAGER_PEER,
                    reviewee='sw3',
                    reviewer='tl1',
                    filename='whatever',
                    line_number=10,
                    eval_response=[])
            ],
            self.reviewers['tl2'].uid: [],
            self.reviewers['sw1'].uid: [],
            self.reviewers['sw2'].uid: [],
            self.reviewers['sw3'].uid: [],
        }

        # when:
        completed, pending, inconsistent = self.sut.get_status_from_responses(
            self.reviewers,
            responses)

        # then:
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
        # given;
        self.sut.set_employees_by_manager(self.employees_by_manager)
        responses = {
            self.reviewers['cto'].uid: [
                ReviewerResponse(
                    eval_kind=EvalKind.MANAGER_PEER,
                    reviewee='tl1',
                    reviewer='cto',
                    filename='',
                    line_number=0,
                    eval_response=[]),
                ReviewerResponse(
                    eval_kind=EvalKind.MANAGER_PEER,
                    reviewee='tl2',
                    reviewer='cto',
                    filename='',
                    line_number=0,
                    eval_response=[])
            ],
            self.reviewers['tl1'].uid: [
                ReviewerResponse(
                    eval_kind=EvalKind.MANAGER_PEER,
                    reviewee='sw1',
                    reviewer='tl1',
                    filename='',
                    line_number=0,
                    eval_response=[]),
                ReviewerResponse(
                    eval_kind=EvalKind.MANAGER_PEER,
                    reviewee='sw2',
                    reviewer='tl1',
                    filename='whatever',
                    line_number=10,
                    eval_response=[])
            ],
            self.reviewers['tl2'].uid: [],
            self.reviewers['sw1'].uid: [
                ReviewerResponse(
                    eval_kind=EvalKind.PEER_MANAGER,
                    reviewee='tl2',
                    reviewer='sw1',
                    filename='whatever',
                    line_number=10,
                    eval_response=[])
            ],
            self.reviewers['sw2'].uid: [],
            self.reviewers['sw3'].uid: [],
        }

        # when:
        completed, pending, inconsistent = self.sut.get_status_from_responses(
            self.reviewers,
            responses)

        # then:
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

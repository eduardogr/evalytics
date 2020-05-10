from unittest import TestCase

from evalytics.usecases import SetupUseCase
from evalytics.usecases import GetReviewersUseCase, SendEvalUseCase
from evalytics.usecases import GetResponseStatusUseCase
from evalytics.usecases import GenerateEvalReportsUseCase
from evalytics.models import ReviewerResponse

from tests.common.employees import employees_collection
from tests.common.mocks import MockDataRepository, MockConfig
from tests.common.mocks import MockEmployeeAdapter, MockReviewerAdapter
from tests.common.mocks import MockCommunicationsProvider
from tests.common.mocks import GetReviewersUseCaseMock
from tests.common.mocks import MockReviewerResponseFilter

class SetupUseCaseSut(SetupUseCase, MockDataRepository):
    'Inject a mock into the SetupUseCase dependency'

class GetReviewersUseCaseSut(
        GetReviewersUseCase,
        MockDataRepository,
        MockEmployeeAdapter):
    'Inject mocks into GetReviewersUseCase dependencies'

class SendEvalUseCaseSut(
        SendEvalUseCase,
        MockCommunicationsProvider,
        MockEmployeeAdapter,
        MockConfig):
    'Inject mocks into SendEmailUseCase dependencies'

class GetResponseStatusUseCaseSut(
        GetResponseStatusUseCase,
        GetReviewersUseCaseMock,
        MockDataRepository,
        MockReviewerAdapter):
    'Inject mocks into GetResponseStatusUseCase dependencies'

class GenerateEvalReportsUseCaseSut(
        GenerateEvalReportsUseCase,
        MockDataRepository,
        MockEmployeeAdapter,
        MockReviewerResponseFilter):
    'Inject mocks into GenerateEvalReportsUseCaseS dependencies'

class TestSetupUseCase(TestCase):

    def setUp(self):
        self.mock_fileid = 'mockid'
        self.mock_filename = 'mockfolder'
        self.sut = SetupUseCaseSut()

    def test_setup_usecase(self):
        setup = self.sut.setup()

        self.assertEqual(self.mock_fileid, setup.folder.id)
        self.assertEqual(self.mock_filename, setup.folder.name)

class TestGetReviewersUseCase(TestCase):

    def setUp(self):
        self.sut = GetReviewersUseCaseSut()

    def test_get_reviewers_usecase(self):
        reviewers = self.sut.get_reviewers()

        self.assertEqual(
            employees_collection().get('em_email'),
            reviewers['em_email'])

class TestSendEvalUseCase(TestCase):

    def setUp(self):
        self.sut = SendEvalUseCaseSut()

    def test_send_email_usecase(self):
        reviewers = {
            'em_email': employees_collection().get('em_email'),
            'manager_em': employees_collection().get('manager_em'),
        }

        evals_sent, evals_not_sent = self.sut.send_eval(reviewers)

        self.assertIn('em_email', evals_sent)
        self.assertIn('manager_em', evals_sent)
        self.assertEqual(0, len(evals_not_sent))

    def test_send_email_usecase_when_exception(self):
        reviewers = {
            'em_email': employees_collection().get('em_email'),
            'manager_em': employees_collection().get('manager_em'),
        }
        self.sut.add_raise_exception_for_reviewer(reviewers['manager_em'].uid)

        evals_sent, evals_not_sent = self.sut.send_eval(reviewers)

        self.assertIn('em_email', evals_sent)
        self.assertEqual(1, len(evals_sent))

        self.assertIn('manager_em', evals_not_sent)
        self.assertEqual(1, len(evals_not_sent))

class TestGetResponseStatusUseCase(TestCase):

    def setUp(self):
        self.sut = GetResponseStatusUseCaseSut()


    def test_get_response_status(self):
        status = self.sut.get_response_status()

class TestGenerateEvalReportsUseCase(TestCase):

    def setUp(self):
        self.sut = GenerateEvalReportsUseCaseSut()

        self.any_reviewer_response = ReviewerResponse(
            'reviewee',
            'reviewer',
            'eval_kind',
            [],
            'filename',
            0
        )
        self.evaluations_response = {
            'uid1': self.any_reviewer_response,
            'uid2': self.any_reviewer_response,
            'uid3': self.any_reviewer_response,
        }


    def test_get_response_status(self):
        dry_run = False
        eval_process_id = ''
        area = ''
        managers = []
        employee_uids = []
        self.sut.set_evaluations_response(self.evaluations_response)

        created, not_created = self.sut.generate(
            dry_run,
            eval_process_id,
            area,
            managers,
            employee_uids
        )

        self.assertEqual(0, len(not_created))
        self.assertEqual(3, len(created))

    def test_get_response_status_when_exceptions_is_raised(self):
        dry_run = False
        eval_process_id = ''
        area = ''
        managers = []
        employee_uids = []
        self.sut.set_evaluations_response(self.evaluations_response)
        self.sut.get_evaluations_will_raise_exception_for_reviewee('uid1')

        created, not_created = self.sut.generate(
            dry_run,
            eval_process_id,
            area,
            managers,
            employee_uids
        )

        self.assertEqual(1, len(not_created))
        self.assertEqual(2, len(created))

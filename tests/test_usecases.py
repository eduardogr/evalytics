from unittest import TestCase

from evalytics.usecases import SetupUseCase
from evalytics.usecases import GetReviewersUseCase, SendEvalUseCase
from evalytics.usecases import GetResponseStatusUseCase
from evalytics.usecases import GenerateEvalReportsUseCase
from evalytics.usecases import GetPeersAssignmentUseCase
from evalytics.usecases import GeneratePeersAssignmentUseCase
from evalytics.models import ReviewerResponse

from tests.common.employees import employees_collection
from tests.common.mocks import MockStorageFactory
from tests.common.mocks import MockGoogleStorage, MockConfig
from tests.common.mocks import MockEmployeeAdapter, MockReviewerAdapter
from tests.common.mocks import MockCommunicationChannelFactory
from tests.common.mocks import MockFormsPlatformFactory, MockGoogleForms
from tests.common.mocks import MockGmailChannel
from tests.common.mocks import GetReviewersUseCaseMock
from tests.common.mocks import MockReviewerResponseFilter

class SetupUseCaseSut(SetupUseCase, MockStorageFactory):
    'Inject a mock into the SetupUseCase dependency'

class GetReviewersUseCaseSut(
        GetReviewersUseCase,
        MockStorageFactory,
        MockFormsPlatformFactory,
        MockEmployeeAdapter):
    'Inject mocks into GetReviewersUseCase dependencies'

class SendEvalUseCaseSut(
        SendEvalUseCase,
        MockCommunicationChannelFactory,
        MockEmployeeAdapter,
        MockConfig):
    'Inject mocks into SendEmailUseCase dependencies'

class GetResponseStatusUseCaseSut(
        GetResponseStatusUseCase,
        GetReviewersUseCaseMock,
        MockFormsPlatformFactory,
        MockReviewerAdapter):
    'Inject mocks into GetResponseStatusUseCase dependencies'

class GenerateEvalReportsUseCaseSut(
        GenerateEvalReportsUseCase,
        MockStorageFactory,
        MockFormsPlatformFactory,
        MockEmployeeAdapter,
        MockReviewerResponseFilter):
    'Inject mocks into GenerateEvalReportsUseCaseS dependencies'

class GetPeersAssignmentUseCaseSut(
        GetPeersAssignmentUseCase,
        MockStorageFactory,
        MockFormsPlatformFactory,):
    'Inject mocks into GetPeersAssignmentUseCase dependencies'

class GeneratePeersAssignmentUseCaseSut(
        GeneratePeersAssignmentUseCase,
        MockStorageFactory,
        MockFormsPlatformFactory,):
    'Inject mocks into GetPeersAssignmentUseCase dependencies'

class TestSetupUseCase(TestCase):

    def setUp(self):
        self.mock_fileid = 'mockid'
        self.mock_filename = 'mockfolder'
        self.sut = SetupUseCaseSut()
        self.sut.set_storage(MockGoogleStorage())

    def test_setup_usecase(self):
        setup = self.sut.setup()

        self.assertEqual(self.mock_fileid, setup.folder.id)
        self.assertEqual(self.mock_filename, setup.folder.name)

class TestGetReviewersUseCase(TestCase):

    def setUp(self):
        self.sut = GetReviewersUseCaseSut()
        self.sut.set_storage(MockGoogleStorage())
        self.sut.set_forms_platform(MockGoogleForms())

    def test_get_reviewers_usecase(self):
        reviewers = self.sut.get_reviewers()

        self.assertEqual(
            employees_collection().get('em_email'),
            reviewers['em_email'])

class TestSendEvalUseCase(TestCase):

    def setUp(self):
        self.sut = SendEvalUseCaseSut()
        self.communication_channel = MockGmailChannel()
        self.reviewers = {
            'em_email': employees_collection().get('em_email'),
            'manager_em': employees_collection().get('manager_em'),
        }

    def test_send_email_usecase(self):
        self.sut.set_communication_channel(self.communication_channel)

        evals_sent, evals_not_sent = self.sut.send_eval(self.reviewers)

        self.assertIn('em_email', evals_sent)
        self.assertIn('manager_em', evals_sent)
        self.assertEqual(0, len(evals_not_sent))

    def test_send_email_usecase_when_exception(self):
        self.communication_channel.add_raise_exception_for_reviewer(
            self.reviewers['manager_em'].uid
        )
        self.sut.set_communication_channel(self.communication_channel)

        evals_sent, evals_not_sent = self.sut.send_eval(self.reviewers)

        self.assertIn('em_email', evals_sent)
        self.assertEqual(1, len(evals_sent))

        self.assertIn('manager_em', evals_not_sent)
        self.assertEqual(1, len(evals_not_sent))

class TestGetResponseStatusUseCase(TestCase):

    def setUp(self):
        self.sut = GetResponseStatusUseCaseSut()
        self.sut.set_forms_platform(MockGoogleForms())

    def test_get_response_status(self):
        _ = self.sut.get_response_status()

class TestGenerateEvalReportsUseCase(TestCase):

    def setUp(self):
        self.sut = GenerateEvalReportsUseCaseSut()
        self.storage = MockGoogleStorage()
        self.forms_platform = MockGoogleForms()
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

        self.forms_platform.set_evaluations_response(self.evaluations_response)
        self.sut.set_storage(self.storage)
        self.sut.set_forms_platform(self.forms_platform)

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

        self.forms_platform.set_evaluations_response(self.evaluations_response)
        self.storage.get_evaluations_will_raise_exception_for_reviewee('uid1')
        self.sut.set_storage(self.storage)
        self.sut.set_forms_platform(self.forms_platform)

        created, not_created = self.sut.generate(
            dry_run,
            eval_process_id,
            area,
            managers,
            employee_uids
        )

        self.assertEqual(1, len(not_created))
        self.assertEqual(2, len(created))

class TestGetPeersAssignmentUseCase(TestCase):

    def setUp(self):
        self.sut = GetPeersAssignmentUseCaseSut()
        self.storage = MockGoogleStorage()
        self.forms_platform = MockGoogleForms()
        self.sut.set_storage(self.storage)
        self.sut.set_forms_platform(self.forms_platform)

    def test_usecase(self):
        self.sut.get_peers()

class TestGeneratePeersAssignmentUseCase(TestCase):

    def setUp(self):
        self.sut = GeneratePeersAssignmentUseCaseSut()
        self.storage = MockGoogleStorage()
        self.forms_platform = MockGoogleForms()
        self.sut.set_storage(self.storage)
        self.sut.set_forms_platform(self.forms_platform)

    def test_usecase(self):
        self.sut.generate()

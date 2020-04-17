from unittest import TestCase

from evalytics.usecases import SetupUseCase
from evalytics.usecases import GetReviewersUseCase, SendMailUseCase

from tests.common.employees import employees_collection
from tests.common.mocks import MockDataRepository, MockEmployeeAdapter
from tests.common.mocks import MockCommunicationsProvider

class SetupUseCaseSut(SetupUseCase, MockDataRepository):
    'Inject a mock into the SetupUseCase dependency'

class GetReviewersUseCaseSut(
        GetReviewersUseCase,
        MockDataRepository,
        MockEmployeeAdapter):
    'Inject a mock into the GetReviewersUseCase dependency'

class SendMailUseCaseSut(
        SendMailUseCase,
        MockCommunicationsProvider,
        MockEmployeeAdapter):
    'Inject a mock into the SendEmailUseCase dependency'

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

class TestSendMailUseCase(TestCase):

    def setUp(self):
        self.sut = SendMailUseCaseSut()

    def test_send_email_usecase(self):
        reviewers = {
            'em_email': employees_collection().get('em_email'),
            'manager_em': employees_collection().get('manager_em'),
        }

        evals_sent, evals_not_sent = self.sut.send_mail(reviewers)

        self.assertIn('em_email', evals_sent)
        self.assertIn('manager_em', evals_sent)
        self.assertEqual(0, len(evals_not_sent))

    def test_send_email_usecase_when_exception(self):
        reviewers = {
            'em_email': employees_collection().get('em_email'),
            'manager_em': employees_collection().get('manager_em'),
        }
        self.sut.add_raise_exception_for_reviewer(reviewers['manager_em'].uid)

        evals_sent, evals_not_sent = self.sut.send_mail(reviewers)

        self.assertIn('em_email', evals_sent)
        self.assertEqual(1, len(evals_sent))

        self.assertIn('manager_em', evals_not_sent)
        self.assertEqual(1, len(evals_not_sent))

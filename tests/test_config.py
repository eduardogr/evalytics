from unittest import TestCase

from evalytics.config import Config

from tests.common.mocks import MockConfigReader

class ConfigSut(Config, MockConfigReader):
    'Injecting a mock into the Config dependency'

class TestProvidersConfig(TestCase):

    def setUp(self):
        self.sut = ConfigSut()

    def test_read_storage_provider(self):
        provider = self.sut.read_storage_provider()

        self.assertEqual('storage-provider', provider)

    def test_read_communication_channel_provider(self):
        provider = self.sut.read_communication_channel_provider()

        self.assertEqual('comm-provider', provider)

    def test_read_forms_platform_provider(self):
        provider = self.sut.read_forms_platform_provider()

        self.assertEqual('form-provider', provider)

class TestSlackProviderConfig(TestCase):

    def setUp(self):
        self.sut = ConfigSut()

    def test_get_slack_token(self):
        slack_token = self.sut.get_slack_token()
        self.assertEqual("TOKEN::TOKEN", slack_token)

    def test_get_slack_text_param(self):
        slack_text_param = self.sut.get_slack_text_param()
        self.assertEqual('{}', slack_text_param)

    def test_get_slack_channel_param(self):
        slack_channel_param = self.sut.get_slack_channel_param()
        self.assertEqual('@{}', slack_channel_param)

    def test_slack_message_is_direct(self):
        slack_message_is_direct = self.sut.slack_message_is_direct()
        self.assertEqual(True, slack_message_is_direct)

    def test_slack_message_as_user_param(self):
        slack_message_as_user_param = self.sut.slack_message_as_user_param()
        self.assertEqual(True, slack_message_as_user_param)

class TestGmailProviderConfig(TestCase):

    def setUp(self):
        self.sut = ConfigSut()

    def test_read_mail_subject(self):
        mail_subject = self.sut.read_mail_subject()

        self.assertEqual('this is the mail subject', mail_subject)

    def test_read_reminder_mail_subject(self):
        reminder_mail_subject = self.sut.read_reminder_mail_subject()

        self.assertEqual('reminder subject', reminder_mail_subject)

class TestGoogleDriveProviderConfig(TestCase):

    def setUp(self):
        self.sut = ConfigSut()

    def test_read_google_folder(self):
        google_folder = self.sut.read_google_folder()

        self.assertEqual('mock_folder', google_folder)

    def test_read_assignments_folder(self):
        google_folder = self.sut.read_assignments_folder()

        self.assertEqual('mock_assignments_folder', google_folder)

    def test_read_assignments_manager_forms_folder(self):
        google_folder = self.sut.read_assignments_manager_forms_folder()

        self.assertEqual('mock_man_ssignments_folder', google_folder)

    def test_read_google_orgchart(self):
        orgchart = self.sut.read_google_orgchart()

        self.assertEqual('mock_orgchart', orgchart)

    def test_read_google_form_map(self):
        formmap = self.sut.read_google_form_map()

        self.assertEqual('mock_formmap', formmap)

    def test_read_assignments_peers_file(self):
        formmap = self.sut.read_assignments_peers_file()

        self.assertEqual('assignments_peers_file', formmap)

    def test_read_google_responses_folder(self):
        tests_folder = self.sut.read_google_responses_folder()

        self.assertEqual('mock_tests_folder', tests_folder)

    def test_read_google_eval_report_template_id(self):
        template_id = self.sut.read_google_eval_report_template_id()

        self.assertEqual('ID', template_id)

    def test_read_google_eval_report_prefix_name(self):
        prefix = self.sut.read_google_eval_report_prefix_name()

        self.assertEqual('Prefix', prefix)

    def test_read_needed_spreadsheets(self):
        needed_spreachseets = self.sut.read_needed_spreadsheets()

        self.assertEqual([
            'mock_orgchart',
            'mock_formmap'], needed_spreachseets)

class TestConfig(TestCase):

    def setUp(self):
        self.sut = ConfigSut()

    def test_read_company_domain(self):
        domain = self.sut.read_company_domain()

        self.assertEqual('mock_domain.com', domain)


    def test_read_company_number_of_employees(self):
        number_of_employees = self.sut.read_company_number_of_employees()

        self.assertEqual(20, number_of_employees)

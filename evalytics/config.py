import yaml

class ConfigReader:

    CONFIG_FILE = 'config.yaml'

    def read(self):
        with open(self.CONFIG_FILE, 'r') as stream:
            data_loaded = yaml.safe_load(stream)

        return data_loaded

class ProvidersConfig(ConfigReader):

    PROVIDERS = 'providers'

    STORAGE = 'storage'
    COMMUNICATION_CHANNEL = 'communication_channel'
    FORMS_PLATFORM = 'forms_platform'

    GOOGLE_DRIVE = "google_drive"
    GMAIL = "gmail"
    GOOGLE_FORMS = "google_forms"

    def read_storage_provider(self):
        config = super().read()
        return config.get(self.PROVIDERS).get(self.STORAGE)

    def read_communication_channel_provider(self):
        config = super().read()
        return config.get(self.PROVIDERS).get(self.COMMUNICATION_CHANNEL)

    def read_forms_platform_provider(self):
        config = super().read()
        return config.get(self.PROVIDERS).get(self.FORMS_PLATFORM)

class GmailProviderConfig(ConfigReader):

    GMAIL_PROVIDER = 'gmail_provider'

    MAIL_SUBJECT = 'mail_subject'
    REMINDER_MAIL_SUBJECT = 'reminder_mail_subject'

    def read_mail_subject(self):
        config = super().read()
        return config.get(self.GMAIL_PROVIDER).get(self.MAIL_SUBJECT)

    def read_reminder_mail_subject(self):
        config = super().read()
        return config.get(self.GMAIL_PROVIDER).get(self.REMINDER_MAIL_SUBJECT)

class GoogleDriveProviderConfig(ConfigReader):

    GOOGLE_DRIVE_PROVIDER = 'google_drive_provider'

    FOLDER = 'folder'
    FORM_RESPONSES_FOLDER = 'form_responses_folder'

    ORG_CHART = 'org_chart'
    FORM_MAP = 'form_map'

    EVAL_REPORT_TEMPLATE_ID = 'eval_report_template_id'
    EVAL_REPORT_PREFIX_NAME = 'eval_report_prefix_name'

    def read_google_folder(self):
        config = super().read()
        return config.get(self.GOOGLE_DRIVE_PROVIDER).get(self.FOLDER)

    def read_google_orgchart(self):
        config = super().read()
        return config.get(self.GOOGLE_DRIVE_PROVIDER).get(self.ORG_CHART)

    def read_google_form_map(self):
        config = super().read()
        return config.get(self.GOOGLE_DRIVE_PROVIDER).get(self.FORM_MAP)

    def read_google_responses_folder(self):
        config = super().read()
        return config.get(self.GOOGLE_DRIVE_PROVIDER).get(self.FORM_RESPONSES_FOLDER)

    def read_google_eval_report_template_id(self):
        config = super().read()
        return config.get(self.GOOGLE_DRIVE_PROVIDER).get(self.EVAL_REPORT_TEMPLATE_ID)

    def read_google_eval_report_prefix_name(self):
        config = super().read()
        return config.get(
            self.GOOGLE_DRIVE_PROVIDER).get(self.EVAL_REPORT_PREFIX_NAME)

    def read_needed_spreadsheets(self):
        orgchart_filename = self.read_google_orgchart()
        formmap_filename = self.read_google_form_map()
        return [
            orgchart_filename,
            formmap_filename
        ]

class CompanyConfig(ConfigReader):

    COMPANY = 'company'
    DOMAIN = 'domain'
    NUMBER_OF_EMPLOYEES = 'number_of_employees'

    def read_company_domain(self):
        config = super().read()
        return config.get(self.COMPANY).get(self.DOMAIN)

    def read_company_number_of_employees(self):
        config = super().read()
        return config.get(self.COMPANY).get(self.NUMBER_OF_EMPLOYEES)

class Config(
        ProvidersConfig,
        GmailProviderConfig,
        GoogleDriveProviderConfig,
        CompanyConfig):
    'Composition of configs'

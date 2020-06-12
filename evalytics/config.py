import yaml

class ConfigReader:

    CONFIG_FILE = 'config.yaml'

    def read(self):
        with open(self.CONFIG_FILE, 'r') as stream:
            data_loaded = yaml.safe_load(stream)

        return data_loaded

class AppConfig(ConfigReader):

    APP = 'app'
    STORAGE_PROVIDER = 'storage_provider'
    COMMUNICATION_CHANNEL_PROVIDER = 'communication_channel_provider'
    FORMS_PLATFORM_PROVIDER = 'forms_platform_provider'
    MAIL_SUBJECT = 'mail_subject'
    REMINDER_MAIL_SUBJECT = 'reminder_mail_subject'

    STORAGE_PROVIDER_GOOGLE = "google"
    COMMUNICATION_CHANNEL_PROVIDER_GOOGLE = "google"
    FORMS_PLATFORM_PROVIDER_GOOGLE = "google"

    def read_storage_provider(self):
        config = super().read()
        return config.get(self.APP).get(self.STORAGE_PROVIDER)

    def read_communication_channel_provider(self):
        config = super().read()
        return config.get(self.APP).get(self.COMMUNICATION_CHANNEL_PROVIDER)

    def read_forms_platform_provider(self):
        config = super().read()
        return config.get(self.APP).get(self.FORMS_PLATFORM_PROVIDER)

    def read_mail_subject(self):
        config = super().read()
        return config.get(self.APP).get(self.MAIL_SUBJECT)

    def read_reminder_mail_subject(self):
        config = super().read()
        return config.get(self.APP).get(self.REMINDER_MAIL_SUBJECT)

class GoogleConfig(ConfigReader):

    GOOGLE = 'google'
    FOLDER = 'folder'
    ORG_CHART = 'org_chart'
    FORM_MAP = 'form_map'
    FORM_RESPONSES_FOLDER = 'form_responses_folder'
    EVAL_REPORT_TEMPLATE_ID = 'eval_report_template_id'
    EVAL_REPORT_PREFIX_NAME = 'eval_report_prefix_name'

    def read_google_folder(self):
        config = super().read()
        return config.get(self.GOOGLE).get(self.FOLDER)

    def read_google_orgchart(self):
        config = super().read()
        return config.get(self.GOOGLE).get(self.ORG_CHART)

    def read_google_form_map(self):
        config = super().read()
        return config.get(self.GOOGLE).get(self.FORM_MAP)

    def read_google_responses_folder(self):
        config = super().read()
        return config.get(self.GOOGLE).get(self.FORM_RESPONSES_FOLDER)

    def read_google_eval_report_template_id(self):
        config = super().read()
        return config.get(self.GOOGLE).get(self.EVAL_REPORT_TEMPLATE_ID)

    def read_google_eval_report_prefix_name(self):
        config = super().read()
        return config.get(self.GOOGLE).get(self.EVAL_REPORT_PREFIX_NAME)

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

class Config(AppConfig, GoogleConfig, CompanyConfig):
    'Composition of configs'

import yaml

class ConfigReader:

    def read(self, filename: str):
        with open(filename, 'r') as stream:
            data_loaded = yaml.safe_load(stream)

        return data_loaded

class Config(ConfigReader):

    CONFIG_FILE = 'config.yaml'

    APP = 'app'
    MAIL_SUBJECT = 'mail_subject'
    REMINDER_MAIL_SUBJECT = 'reminder_mail_subject'

    GOOGLE = 'google'
    FOLDER = 'folder'
    ORG_CHART = 'org_chart'
    FORM_MAP = 'form_map'
    FORM_RESPONSES_FOLDER = 'form_responses_folder'
    EVAL_REPORT_TEMPLATE_ID = 'eval_report_template_id'
    EVAL_REPORT_PREFIX_NAME = 'eval_report_prefix_name'

    COMPANY = 'company'
    DOMAIN = 'domain'
    NUMBER_OF_EMPLOYEES = 'number_of_employees'


    def read_mail_subject(self):
        config = self.__get_config()
        return config.get(self.APP).get(self.MAIL_SUBJECT)

    def read_reminder_mail_subject(self):
        config = self.__get_config()
        return config.get(self.APP).get(self.REMINDER_MAIL_SUBJECT)

    def read_google_folder(self):
        config = self.__get_config()
        return config.get(self.GOOGLE).get(self.FOLDER)

    def read_google_orgchart(self):
        config = self.__get_config()
        return config.get(self.GOOGLE).get(self.ORG_CHART)

    def read_google_form_map(self):
        config = self.__get_config()
        return config.get(self.GOOGLE).get(self.FORM_MAP)

    def read_google_responses_folder(self):
        config = self.__get_config()
        return config.get(self.GOOGLE).get(self.FORM_RESPONSES_FOLDER)

    def read_google_eval_report_template_id(self):
        config = self.__get_config()
        return config.get(self.GOOGLE).get(self.EVAL_REPORT_TEMPLATE_ID)

    def read_google_eval_report_prefix_name(self):
        config = self.__get_config()
        return config.get(self.GOOGLE).get(self.EVAL_REPORT_PREFIX_NAME)

    def read_needed_spreadsheets(self):
        orgchart_filename = self.read_google_orgchart()
        formmap_filename = self.read_google_form_map()
        return [
            orgchart_filename,
            formmap_filename
        ]

    def read_company_domain(self):
        config = self.__get_config()
        return config.get(self.COMPANY).get(self.DOMAIN)

    def read_company_number_of_employees(self):
        config = self.__get_config()
        return config.get(self.COMPANY).get(self.NUMBER_OF_EMPLOYEES)

    def __get_config(self):
        return super().read(self.CONFIG_FILE)

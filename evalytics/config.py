from configparser import ConfigParser

class Config(ConfigParser):

    CONFIG_FILE = 'config.ini'

    def read_mail_subject(self):
        super().read(self.CONFIG_FILE)
        return super().get('APP', 'mail_subject')

    def read_google_folder(self):
        super().read(self.CONFIG_FILE)
        return super().get('GOOGLE', 'folder')

    def read_google_orgchart(self):
        super().read(self.CONFIG_FILE)
        return super().get('GOOGLE', 'org_chart')

    def read_google_form_map(self):
        super().read(self.CONFIG_FILE)
        return super().get('GOOGLE', 'form_map')

    def read_needed_spreadsheets(self):
        orgchart_filename = self.read_google_orgchart()
        formmap_filename = self.read_google_form_map()
        return [
            orgchart_filename,
            formmap_filename
        ]

    def read_company_domain(self):
        super().read(self.CONFIG_FILE)
        return super().get('COMPANY', 'domain')

    def read_company_number_of_employees(self):
        super().read(self.CONFIG_FILE)
        return super().get('COMPANY', 'number_of_employees',)

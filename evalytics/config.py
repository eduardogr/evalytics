from configparser import ConfigParser


class Config(ConfigParser):

    def read_mail_subject(self):
        super().read('config.ini')
        return super().get('APP', 'MAIL_SUBJECT')

    def read_google_folder(self):
        super().read('config.ini')
        return super().get('GOOGLE', 'FOLDER')

    def read_google_orgchart(self):
        super().read('config.ini')
        return super().get('GOOGLE', 'ORGCHART')

    def read_google_form_map(self):
        super().read('config.ini')
        return super().get('GOOGLE', 'FORM_MAP')

    def read_needed_spreadsheets(self):
        orgchart_filename = self.read_google_orgchart()
        formmap_filename = self.read_google_form_map()
        return [
            orgchart_filename,
            formmap_filename
        ]

    def read_company_domain(self):
        super().read('config.ini')
        return super().get('COMPANY', 'DOMAIN')

    def read_company_number_of_employees(self):
        super().read('config.ini')
        return super().get('COMPANY', 'NUMBER_OF_EMPLOYEES')

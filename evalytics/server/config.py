from configparser import ConfigParser


class Config(ConfigParser):

    def read_google_folder(self):
        super().read('config.ini')
        return super().get('GOOGLE', 'FOLDER')

    def read_google_orgchart(self):
        super().read('config.ini')
        return super().get('GOOGLE', 'ORGCHART')

    def read_google_form_map(self):
        super().read('config.ini')
        return super().get('GOOGLE', 'FORM_MAP')

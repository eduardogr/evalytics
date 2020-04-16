from configparser import ConfigParser
from unittest import TestCase

from evalytics.config import Config

class MockConfigParser(ConfigParser):

    def read(self, filename: str = ''):
        return {
            'GOOGLE': {
                'FOLDER': 'mock_folder',
                'ORGCHART': 'mock_orgchart',
                'FORM_MAP': 'mock_formmap',
            },
            'COMPANY': {
                'DOMAIN': 'mock_domain.com',
                'NUMBER_OF_EMPLOYEES': 20,
            }
        }

    def get(self, key, section):
        return self.read()[key][section]

class ConfigSut(Config, MockConfigParser):
    'Injecting mock in Config dependency'

class TestConfig(TestCase):

    def test_read_google_folder(self):
        config = ConfigSut()

        google_folder = config.read_google_folder()

        self.assertEqual('mock_folder', google_folder)

    def test_read_google_orgchart(self):
        config = ConfigSut()

        orgchart = config.read_google_orgchart()

        self.assertEqual('mock_orgchart', orgchart)

    def test_read_google_form_map(self):
        config = ConfigSut()

        formmap = config.read_google_form_map()

        self.assertEqual('mock_formmap', formmap)

    def test_read_needed_spreadsheets(self):
        config = ConfigSut()

        needed_spreachseets = config.read_needed_spreadsheets()

        self.assertEqual([
            'mock_orgchart',
            'mock_formmap'], needed_spreachseets)

    def test_rread_company_domain(self):
        config = ConfigSut()

        domain = config.read_company_domain()

        self.assertEqual('mock_domain.com', domain)


    def test_read_company_number_of_employees(self):
        config = ConfigSut()

        number_of_employees = config.read_company_number_of_employees()

        self.assertEqual(20, number_of_employees)

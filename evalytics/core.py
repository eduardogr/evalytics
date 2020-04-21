from .models import Reviewer
from .storages import GoogleStorage
from .communications_channels import GmailChannel

class DataRepository(GoogleStorage):

    def setup_storage(self):
        return super().setup()

    def get_employees(self):
        return super().get_employee_map()

    def get_forms(self):
        return super().get_forms_map()

    def get_responses(self):
        return super().get_responses_map()

    def get_evaluations(self):
        return super().get_evaluations_map()

class CommunicationsProvider(GmailChannel):

    def send_communication(self, reviewer: Reviewer, mail_subject: str, data):
        return super().send(reviewer, mail_subject, data)

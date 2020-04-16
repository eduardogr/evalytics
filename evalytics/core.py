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

class CommunicationsProvider(GmailChannel):

    def send_communication(self, reviewer: Reviewer, data):
        return super().send(reviewer, data)

from .models import Setup, Employee
from .storages import GoogleStorage
from .communications_channels import GmailChannel

class DataRepository(GoogleStorage):

    def setup_storage(self) -> Setup:
        return super().setup()

    def get_employees(self):
        return super().get_employee_list()

class CommunicationsProvider(GmailChannel):

    def send_communication(self, employee: Employee, data):
        return super().send(employee, data)

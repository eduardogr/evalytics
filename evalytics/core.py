from .models import Reviewer, ReviewerResponse
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

    def generate_eval_reports(self,
                              dry_run,
                              eval_process_id,
                              reviewee,
                              reviewee_evaluations: ReviewerResponse,
                              employee_managers):
        return super().generate_eval_reports_in_storage(
            dry_run,
            eval_process_id,
            reviewee,
            reviewee_evaluations,
            employee_managers)

class CommunicationsProvider(GmailChannel):

    def send_communication(self, reviewer: Reviewer, mail_subject: str, data):
        return super().send(reviewer, mail_subject, data)

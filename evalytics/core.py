from .models import Reviewer, ReviewerResponse
from .storages import StorageFactory
from .communications_channels import CommunicationChannelFactory

class DataRepository(StorageFactory):

    def setup_storage(self):
        return super().get_storage().setup()

    def get_employees(self):
        return super().get_storage().get_employee_map()

    def get_forms(self):
        return super().get_storage().get_forms_map()

    def get_responses(self):
        return super().get_storage().get_responses_map()

    def get_evaluations(self):
        return super().get_storage().get_evaluations_map()

    def generate_eval_reports(self,
                              dry_run,
                              eval_process_id,
                              reviewee,
                              reviewee_evaluations: ReviewerResponse,
                              employee_managers):
        return super().get_storage().generate_eval_reports_in_storage(
            dry_run,
            eval_process_id,
            reviewee,
            reviewee_evaluations,
            employee_managers)

class CommunicationsProvider(CommunicationChannelFactory):

    def send_communication(self, reviewer: Reviewer, mail_subject: str, data):
        return super().get_communication_channel().send(reviewer, mail_subject, data)

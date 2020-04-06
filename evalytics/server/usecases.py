from .adapters import EmployeeAdapter
from .core import DataRepository, CommunicationsProvider

class SetupUseCase(DataRepository):

    def execute(self):
        setup = super().setup_storage()
        return setup

class GetReviewersUseCase(DataRepository, EmployeeAdapter):

    def execute(self):
        return super().build_reviewers(
            super().get_employees(),
            super().get_forms())


class SendEmailUseCase(CommunicationsProvider, EmployeeAdapter):

    def execute(self, revieweers):
        for _, reviewer in revieweers.items():
            super().send_communication(
                employee=reviewer,
                data=super().build_eval_message(reviewer))

        return revieweers

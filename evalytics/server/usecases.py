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

class SendMailUseCase(CommunicationsProvider, EmployeeAdapter):

    def send_mail(self, revieweers):
        evals_sent = []
        evals_not_sent = []
        for _, reviewer in revieweers.items():
            try:
                super().send_communication(
                    reviewer=reviewer,
                    data=super().build_eval_message(reviewer))
                evals_sent.append(reviewer.uid)
            except:
                evals_not_sent.append(reviewer.uid)

        return evals_sent, evals_not_sent

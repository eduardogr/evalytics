from evalytics.models import CommunicationKind
from evalytics.adapters import EmployeeAdapter, ReviewerAdapter
from evalytics.filters import ReviewerResponseFilter
from evalytics.storages import StorageFactory
from evalytics.communications_channels import CommunicationChannelFactory
from evalytics.forms import FormsPlatformFactory

class SetupUseCase(StorageFactory):

    def setup(self):
        storage = super().get_storage()
        setup = storage.setup()
        return setup

class GetReviewersUseCase(
        StorageFactory,
        FormsPlatformFactory,
        EmployeeAdapter):

    def get_reviewers(self):
        storage = super().get_storage()
        forms_platform = super().get_forms_platform()
        return super().build_reviewers(
            storage.get_employees(),
            forms_platform.get_peers_assignment()['peers'],
            storage.get_forms())

class SendCommunicationUseCase(CommunicationChannelFactory):

    def send(self, revieweers, kind: CommunicationKind):
        communication_channel = super().get_communication_channel()

        comm_sent = []
        comm_not_sent = []
        for _, reviewer in revieweers.items():
            try:
                communication_channel.send_communication(
                    reviewer=reviewer,
                    kind=kind)
                comm_sent.append(reviewer.uid)
            except:
                comm_not_sent.append(reviewer.uid)

        return comm_sent, comm_not_sent

class SendEvalUseCase(CommunicationChannelFactory):

    def send_eval(self, revieweers, is_reminder: bool = False):
        communication_channel = super().get_communication_channel()

        communication_kind = CommunicationKind.PROCESS_STARTED
        if is_reminder:
            communication_kind = CommunicationKind.PENDING_EVALS_REMINDER

        evals_sent = []
        evals_not_sent = []
        for _, reviewer in revieweers.items():
            try:
                communication_channel.send_communication(
                    reviewer=reviewer,
                    kind=communication_kind)
                evals_sent.append(reviewer.uid)
            except:
                evals_not_sent.append(reviewer.uid)

        return evals_sent, evals_not_sent

class GetResponseStatusUseCase(
        GetReviewersUseCase, FormsPlatformFactory, ReviewerAdapter):

    def get_response_status(self):
        reviewers = super().get_reviewers()
        responses = super().get_forms_platform().get_responses()
        return super().get_status_from_responses(reviewers, responses)

class GenerateEvalReportsUseCase(
        StorageFactory, FormsPlatformFactory,
        EmployeeAdapter, ReviewerResponseFilter):

    def generate(
            self,
            dry_run,
            eval_process_id,
            area, managers,
            employee_uids):
        storage = super().get_storage()
        forms_platform = super().get_forms_platform()

        reviewee_evaluations = forms_platform.get_evaluations()
        employees = storage.get_employees()

        reviewee_evaluations = super().filter_reviewees(
            reviewee_evaluations,
            employees,
            area,
            managers,
            employee_uids)

        created = {}
        not_created = {}
        for uid, reviewee_evaluations in reviewee_evaluations.items():
            employee_managers = super().get_employee_managers(employees, uid)

            try:
                storage.generate_eval_reports(
                    dry_run,
                    eval_process_id,
                    uid,
                    reviewee_evaluations,
                    employee_managers)

                created.update({
                    uid: {
                        'employee': uid,
                        'managers': employee_managers
                    }
                })
            except:
                not_created.update({
                    uid: {
                        'employee': uid,
                        'managers': employee_managers
                    }
                })

        return created, not_created

class GetPeersAssignmentUseCase(StorageFactory, FormsPlatformFactory):

    def get_peers(self):
        forms_platform = super().get_forms_platform()
        return forms_platform.get_peers_assignment()

class GeneratePeersAssignmentUseCase(StorageFactory, FormsPlatformFactory):

    def generate(self):
        storage = super().get_storage()
        forms_platform = super().get_forms_platform()

        peers_assignment = forms_platform.get_peers_assignment()['peers']
        storage.write_peers_assignment(peers_assignment)

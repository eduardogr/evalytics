from evalytics.adapters import EmployeeAdapter, ReviewerAdapter
from evalytics.filters import ReviewerResponseFilter
from evalytics.core import DataRepository, CommunicationsProvider
from evalytics.config import Config

class SetupUseCase(DataRepository):

    def setup(self):
        setup = super().setup_storage()
        return setup

class GetReviewersUseCase(DataRepository, EmployeeAdapter):

    def get_reviewers(self):
        return super().build_reviewers(
            super().get_employees(),
            super().get_forms())

class SendEvalUseCase(CommunicationsProvider, EmployeeAdapter, Config):

    def send_eval(self, revieweers, is_reminder: bool = False):
        if is_reminder:
            mail_subject = super().read_reminder_mail_subject()
            message = 'You have pending evals:'
        else:
            mail_subject = super().read_mail_subject()
            message = 'You have new assignments !'

        evals_sent = []
        evals_not_sent = []
        for _, reviewer in revieweers.items():
            try:
                super().send_communication(
                    reviewer=reviewer,
                    mail_subject=mail_subject,
                    data=super().build_message(message, reviewer))
                evals_sent.append(reviewer.uid)
            except:
                evals_not_sent.append(reviewer.uid)

        return evals_sent, evals_not_sent

class GetResponseStatusUseCase(
        GetReviewersUseCase, DataRepository, ReviewerAdapter):

    def get_response_status(self):
        reviewers = super().get_reviewers()
        responses = super().get_responses()
        return super().get_status_from_responses(reviewers, responses)

class GenerateEvalReportsUseCase(
        DataRepository, EmployeeAdapter, ReviewerResponseFilter):

    def generate(
            self,
            dry_run,
            eval_process_id,
            area, managers,
            employee_uids):
        reviewee_evaluations = super().get_evaluations()
        employees = super().get_employees()

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
                super().generate_eval_reports(
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

from .adapters import EmployeeAdapter
from .core import DataRepository, CommunicationsProvider

class SetupUseCase(DataRepository):

    def execute(self):
        setup = super().setup_storage()
        return setup

class StartUseCase(DataRepository, CommunicationsProvider, EmployeeAdapter):

    def execute(self):
        employees = super().get_employees()
        forms = super().get_forms()

        reviewers = []
        employees = super().add_evals(employees, forms)
        for employee in employees:
        #    super().send_communication(
        #        employee=employee,
        #        data=super().build_eval_message(employee))
            reviewers.append(employee)

        return employees


class GetEvaluationStatusUseCase:

    def get(self):
        pass

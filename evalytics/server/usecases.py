from .adapters import EmployeeAdapter
from .core import DataRepository, CommunicationsProvider

class SetupUseCase(DataRepository):

    def execute(self):
        setup = super().setup_storage()
        return setup

class StartUseCase(DataRepository, CommunicationsProvider, EmployeeAdapter):

    def execute(self):
        employees = super().get_employees()

        reviews = []
        for employee in employees:
            super().send_communication(
                employee=employee,
                data=super().build_eval_message(employee))
            reviews.append(employee)

        return reviews


class GetEvaluationStatusUseCase:

    def get(self):
        pass

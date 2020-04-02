from .adapters import EmployeeAdapter
from .core import DataRepository, CommunicationsProvider

class SetupUseCase:

    def execute(self):
        repository = DataRepository()
        setup = repository.setup()
        return setup

class StartUseCase:

    def execute(self):
        repository = DataRepository()
        comms_provider = CommunicationsProvider()

        employees = repository.get_employees()

        reviews = []
        for employee in employees:
            comms_provider.send_communication(
                employee=employee,
                data=EmployeeAdapter.build_eval_message(employee))
            reviews.append(employee)

        return reviews


class GetEvaluationStatusUseCase:

    def get(self):
        pass

from .adapters import EmployeeAdapter

class StartEvaluationProcess:

    __repository = None

    def __init__(self, repository):
        self.__repository = repository

    def start(self):
        employees = self.__repository.get_employee_list()
        EmployeeAdapter.build_org_chart(employees)


class GetEvaluationProcessStatus:

    __repository = None

    def __init__(self, repository):
        self.__repository = repository

    def get(self):
        pass

from .adapters import EmployeeAdapter

class StartEvaluationProcess:

    __repository = None
    __comms_provider = None

    def __init__(self, repository, comms_provider):
        self.__repository = repository
        self.__comms_provider = comms_provider

    def start(self):
        employees = self.__repository.get_employee_list()
        EmployeeAdapter.build_org_chart(employees)

        # TODO: get reviewer -> reviewees list.
        # Called InitialEvals
        reviews = employees
        for employee in reviews:
            self.__comms_provider.send(employee.mail, {})


class GetEvaluationProcessStatus:

    __repository = None

    def __init__(self, repository):
        self.__repository = repository

    def get(self):
        pass

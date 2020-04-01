from .adapters import EmployeeAdapter


class SetupUseCase:

    __repository = None
    __comms_provider = None

    def __init__(self, repository, comms_provider):
        self.__repository = repository
        self.__comms_provider = comms_provider

    def execute(self):
        setup = self.__repository.setup()
        return setup

class StartUseCase:

    __repository = None
    __comms_provider = None

    def __init__(self, repository, comms_provider):
        self.__repository = repository
        self.__comms_provider = comms_provider

    def execute(self):
        employees = self.__repository.get_employee_list()

        reviews = []
        for employee in employees:
            reviews.append(employee)

        return reviews


class GetEvaluationStatusUseCase:

    __repository = None

    def __init__(self, repository):
        self.__repository = repository

    def get(self):
        pass

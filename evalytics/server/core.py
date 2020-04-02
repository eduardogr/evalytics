from .models import Setup, Employee

class DataRepository:

    def __init__(self, storage):
        self.__storage = storage

    def setup(self) -> Setup:
        return self.__storage.setup()

    def get_employee_list(self):
        return self.__storage.get_employee_list()

class CommunicationsProvider:

    def __init__(self, communication_channel):
        self.__communication_channel = communication_channel

    def send(self, employee: Employee, data):
        return self.__communication_channel.send(employee, data)

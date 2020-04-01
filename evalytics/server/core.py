

class DataRepository:

    def __init__(self, storage):
        self.__storage = storage

    def get_employee_list(self):
        return self.__storage.get_employee_list()

class CommunicationsProvider:

    def __init__(self, communication_channel):
        self.__communication_channel = communication_channel

    def send(self, destiny, data):
        return self.__communication_channel.send(destiny, data)

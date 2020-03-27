

class DataRepository:

    def __init__(self, storage):
        self.__storage = storage

    def get_employee_list(self):
        return self.__storage.get_employee_list()

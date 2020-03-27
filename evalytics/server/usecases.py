class StartEvaluationProcess:

    __reader = None

    def __init__(self, reader):
        self.__reader = reader

    def start(self, id):
        self.__reader.get_org_chart()
        pass


class GetEvaluationProcessStatus:

    __reader = None

    def __init__(self, reader):
        self.__reader = reader

    def get(self, id):
        pass

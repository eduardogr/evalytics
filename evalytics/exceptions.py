class MissingDataException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'MissingDataException, {0} '.format(self.message)
        else:
            return 'MissingDataException has been raised'

class NoFormsException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'NoFormsException, {0} '.format(self.message)
        else:
            return 'NoFormsException has been raised'

class NotExistentEmployeeException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'NotExistentEmployeException, {0} '.format(self.message)
        else:
            return 'NotExistentEmployeException has been raised'

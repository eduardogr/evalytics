class CustomException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def get_str(self, class_name):
        if self.message:
            return '{0}, {1} '.format(self.message, class_name)
        else:
            return '{0} has been raised'.format(class_name)

class NotExistentGoogleDriveFolderException(CustomException):

    def __str__(self):
        return super().get_str('NotExistentGoogleDriveFolderException')

class MissingDataException(CustomException):

    def __str__(self):
        return super().get_str('MissingDataException')

class NoFormsException(CustomException):

    def __str__(self):
        return super().get_str('NoFormsException')

class NotExistentEmployeeException(CustomException):

    def __str__(self):
        return super().get_str('NotExistentEmployeeException')

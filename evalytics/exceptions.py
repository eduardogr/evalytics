from evalytics.models import GoogleApiClientHttpError

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

class GoogleApiClientHttpErrorException(Exception):
    def __init__(self, google_api_client_http_error: GoogleApiClientHttpError):
        self.google_api_client_http_error = google_api_client_http_error

    def get_google_api_client_http_error(self):
        return self.google_api_client_http_error

class CommunicationChannelException(CustomException):

    def __str__(self):
        return super().get_str('CommunicationChannelException')

class MissingGoogleDriveFolderException(CustomException):

    def __str__(self):
        return super().get_str('MissingGoogleDriveFolderException')

class MissingGoogleDriveFileException(CustomException):

    def __str__(self):
        return super().get_str('MissingGoogleDriveFileException')

class MissingDataException(CustomException):

    def __str__(self):
        return super().get_str('MissingDataException')

class NoFormsException(CustomException):

    def __str__(self):
        return super().get_str('NoFormsException')

class NoPeersException(CustomException):

    def __str__(self):
        return super().get_str('NoPeersException')

class NotExistentEmployeeException(CustomException):

    def __str__(self):
        return super().get_str('NotExistentEmployeeException')

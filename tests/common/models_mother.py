from evalytics.models import GoogleFile, GoogleSetup
from evalytics.models import EvalKind, Eval
from evalytics.models import Employee, Reviewer
from evalytics.models import GoogleApiClientHttpError

class GoogleFileMother:

    def get_any_google_file_model(self):
        any_name = 'name'
        any_id = 'ID'
        return GoogleFile(
            name=any_name,
            id=any_id
        )

class GoogleSetupMother:

    def get_any_google_setup_model(self, with_files_number: int):
        any_folder = GoogleFileMother().get_any_google_file_model()
        any_files = []

        for _ in range(0, with_files_number):
            any_files.append(any_folder)

        return GoogleSetup(
            any_folder,
            any_files
        )

class EvalMother:

    def get_any_eval_model(self):
        return Eval(
            reviewee='employee_uid',
            kind=EvalKind.SELF,
            form='my_form'
        )

class EmployeeMother:

    def get_any_employee_model(self):
        return Employee(
            mail='some@employee.com',
            manager='manager',
            area='Area'
        )

class ReviewerMother:

    def get_any_reviewer_model(self):
        employee = Employee(
            mail='some@employee.com',
            manager='manager',
            area='Area'
        )
        return Reviewer(
            employee=employee,
            evals=[]
        )

class GoogleApiClientHttpErrorMother:

    def get_any_google_api_client_http_error__model(self):
        code = 200
        message = "This is your friendly human-based text message"
        status = 201
        details = []

        return GoogleApiClientHttpError(
            code,
            message,
            status,
            details)

class Mother(
        GoogleFileMother,
        GoogleSetupMother,
        EvalMother,
        EmployeeMother,
        ReviewerMother,
        GoogleApiClientHttpErrorMother):
    'Composition of mother classes'

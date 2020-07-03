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

class EmployeeFixture:

    def get_organization(self):
        ceo = EmployeeMother().create_employee('ceo', '')
        cto = EmployeeMother().create_employee('cto', 'ceo')
        tl1 = EmployeeMother().create_employee('tl1', 'cto')
        tl2 = EmployeeMother().create_employee('tl2', 'cto')
        sw1 = EmployeeMother().create_employee('sw1', 'tl1')
        sw2 = EmployeeMother().create_employee('sw2', 'tl1')
        sw3 = EmployeeMother().create_employee('sw3', 'tl2')
        sw4 = EmployeeMother().create_employee('sw4', 'tl2')
        sw5 = EmployeeMother().create_employee('sw5', 'tl2')
        employees = {
            'ceo': ceo,
            'cto': cto,
            'tl1': tl1,
            'tl2': tl2,
            'sw1': sw1,
            'sw2': sw2,
            'sw3': sw3,
            'sw4': sw4,
            'sw5': sw5,
        }
        return employees

    def get_organization_employees_by_managers(self):
        return {
            'ceo': ['cto'],
            'cto': ['tl1', 'tl2'],
            'tl1': ['sw1', 'sw2'],
            'tl2': ['sw3']
        }

class EmployeeMother:

    def create_employee(self, uid, manager):
        return Employee(
            mail='{}@company.com'.format(uid),
            manager=manager,
            area='Eng'
        )

    def get_any_employee_model(self):
        return Employee(
            mail='some@employee.com',
            manager='manager',
            area='Area'
        )

class ReviewerMother:

    def get_organization_reviewers(self):
        any_form = 'https://i am a form and you trust me'
        organization = EmployeeFixture().get_organization()
        return {
            organization['cto'].uid: Reviewer(
                employee=organization['cto'],
                evals=[
                    Eval(reviewee='tl1', kind=EvalKind.MANAGER_PEER, form=any_form),
                    Eval(reviewee='tl2', kind=EvalKind.MANAGER_PEER, form=any_form),
                ]
            ),
            organization['tl1'].uid: Reviewer(
                employee=organization['tl1'],
                evals=[
                    Eval(reviewee='cto', kind=EvalKind.PEER_MANAGER, form=any_form),
                    Eval(reviewee='tl1', kind=EvalKind.SELF, form=any_form),
                    Eval(reviewee='sw1', kind=EvalKind.MANAGER_PEER, form=any_form),
                    Eval(reviewee='sw2', kind=EvalKind.MANAGER_PEER, form=any_form),
                ]
            ),
            organization['tl2'].uid: Reviewer(
                employee=organization['tl2'],
                evals=[
                    Eval(reviewee='cto', kind=EvalKind.PEER_MANAGER, form=any_form),
                    Eval(reviewee='tl2', kind=EvalKind.SELF, form=any_form),
                    Eval(reviewee='sw3', kind=EvalKind.MANAGER_PEER, form=any_form),
                ]
            ),
            organization['sw1'].uid: Reviewer(
                employee=organization['sw1'],
                evals=[
                    Eval(reviewee='sw1', kind=EvalKind.SELF, form=any_form),
                    Eval(reviewee='tl1', kind=EvalKind.PEER_MANAGER, form=any_form),
                ]
            ),
            organization['sw2'].uid: Reviewer(
                employee=organization['sw2'],
                evals=[
                    Eval(reviewee='sw2', kind=EvalKind.SELF, form=any_form),
                    Eval(reviewee='tl1', kind=EvalKind.PEER_MANAGER, form=any_form),
                ]
            ),
            organization['sw3'].uid: Reviewer(
                employee=organization['sw3'],
                evals=[
                    Eval(reviewee='sw3', kind=EvalKind.SELF, form=any_form),
                    Eval(reviewee='tl2', kind=EvalKind.PEER_MANAGER, form=any_form),
                ]
            )
        }

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

class Fixture(
        GoogleFileMother,
        GoogleSetupMother,
        EvalMother,
        EmployeeMother,
        EmployeeFixture,
        ReviewerMother,
        GoogleApiClientHttpErrorMother):
    'Composition of mother classes'

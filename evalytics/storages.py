from evalytics.google_api import GoogleAPI
from evalytics.config import Config
from evalytics.models import GoogleSetup, GoogleFile
from evalytics.models import Employee, EvalKind
from evalytics.models import ReviewerResponse
from evalytics.exceptions import MissingDataException, NoFormsException

class StorageFactory(Config):

    def get_storage(self):
        storage_kind = super().read_storage_provider()
        if storage_kind == Config.STORAGE_PROVIDER_GOOGLE:
            return GoogleStorage()

        raise ValueError(storage_kind)

class GoogleStorage(GoogleAPI, Config):

    FORM_MAP_RANGE = 'A2:D3'

    def setup(self):
        folder_name = super().read_google_folder()
        needed_spreadsheets = super().read_needed_spreadsheets()

        # Folder setup
        folder = super().get_folder(name=folder_name)
        if folder is None:
            folder = super().create_folder(name=folder_name)

        folder_parent = folder.get('parents')[0]

        # Sheet setup
        files = []
        for filename in needed_spreadsheets:
            spreadheet_id = super().get_file_id_from_folder(
                folder_id=folder.get('id'),
                filename=filename)

            if spreadheet_id is None:
                spreadheet_id = super().create_sheet(
                    folder=folder,
                    folder_parent=folder_parent,
                    filename=filename
                )
            files.append(GoogleFile(name=filename, id=spreadheet_id))

        folder = GoogleFile(name=folder_name, id=folder.get('id'))
        return GoogleSetup(
            folder=folder,
            files=files)

    def get_employees(self):
        employees = {}
        number_of_employees = int(super().read_company_number_of_employees())

        if number_of_employees == 0:
            return employees

        org_chart_range = 'A2:C' + str(number_of_employees + 1)
        values = super().get_file_rows_from_folder(
            foldername=super().read_google_folder(),
            filename=super().read_google_orgchart(),
            rows_range=org_chart_range)
        company_domain = super().read_company_domain()

        # Creating models
        for row in values:
            if len(row) < 3:
                raise MissingDataException("Missing data in employees, row: %s" % (row))

            employee_uid = row[0].strip()
            employee_mail = employee_uid + '@' + company_domain
            manager = row[1].strip()
            area = row[2].strip()

            employee = Employee(
                mail=employee_mail,
                manager=manager,
                area=area)
            employees.update({employee.uid : employee})

        return employees

    def get_forms(self):
        values = super().get_file_rows_from_folder(
            foldername=super().read_google_folder(),
            filename=super().read_google_form_map(),
            rows_range=self.FORM_MAP_RANGE)

        if len(values) == 0:
            raise NoFormsException("Missing forms in google")

        # Creating models
        forms = {}
        for row in values:
            if len(row) < 4:
                raise MissingDataException("Missing data in forms, row: %s" % (row))

            form_area = row[0].strip()
            self_eval = row[1]
            peer_manager_eval = row[2]
            manager_peer_eval = row[3]

            forms.update({
                form_area: {
                    EvalKind.SELF: self_eval,
                    EvalKind.PEER_MANAGER: peer_manager_eval,
                    EvalKind.MANAGER_PEER: manager_peer_eval,
                }
            })            

        return forms

    def generate_eval_reports(self,
                              dry_run,
                              eval_process_id,
                              reviewee,
                              reviewee_evaluations: ReviewerResponse,
                              employee_managers):
        template_id = super().read_google_eval_report_template_id()
        filename_prefix = super().read_google_eval_report_prefix_name()
        filename = '{} {}'.format(filename_prefix, reviewee)

        company_domain = super().read_company_domain()
        employee_managers = [
            '{}@{}'.format(m, company_domain)
            for m in employee_managers
        ]

        document_id = super().copy_file(template_id, filename)

        super().insert_eval_report_in_document(
            eval_process_id,
            document_id,
            reviewee,
            reviewee_evaluations)

        if dry_run:
            return employee_managers

        else:
            super().add_comenter_permission(
                document_id,
                employee_managers
            )
            return employee_managers

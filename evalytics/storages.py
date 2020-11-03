from evalytics.google_api import GoogleAPI, GoogleDrive
from evalytics.config import Config, ProvidersConfig
from evalytics.models import Employee, EvalKind
from evalytics.models import ReviewerResponse
from evalytics.exceptions import MissingDataException, NoFormsException
from evalytics.exceptions import NoPeersException

class StorageFactory(Config):

    def get_storage(self):
        storage_kind = super().read_storage_provider()
        if storage_kind == ProvidersConfig.GOOGLE_DRIVE:
            return GoogleStorage()

        raise ValueError(storage_kind)

class GoogleStorage(GoogleAPI, Config):

    def get_employees(self):
        google_folder = super().read_google_folder()
        org_chart = super().read_google_orgchart()
        org_chart_range = super().read_google_orgchart_range()
        company_domain = super().read_company_domain()

        employees = {}

        # TODO:
        # file = super().open('/google_folder/org_chart', "r")
        # values = file.readlines(org_chart_range): // podría no especificarse el rango y leer hasta que ... X
        # for row in values:
        #
        values = super().get_file_rows_from_folder(
            foldername=google_folder,
            filename=org_chart,
            rows_range=org_chart_range)

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
        google_folder = super().read_google_folder()
        google_form_map = super().read_google_form_map()
        google_form_map_range = super().read_google_form_map_range()

        # TODO:
        # file = super().open('/google_folder/google_form_map', "r")
        # values = file.readlines(google_form_map_range): // podría no especificarse el rango y leer hasta que ... X
        # for row in values:
        #
        values = super().get_file_rows_from_folder(
            foldername=google_folder,
            filename=google_form_map,
            rows_range=google_form_map_range)

        if len(values) == 0:
            raise NoFormsException('File <{}> is empty'.format(google_form_map))

        # Creating models
        forms = {}
        for row in values:
            if len(row) < 5:
                raise MissingDataException("Missing data in forms, row: %s" % (row))

            form_area = row[0].strip()
            self_eval = row[1]
            peer_manager_eval = row[2]
            manager_peer_eval = row[3]
            peer_to_peer_eval = row[4]

            forms.update({
                form_area: {
                    EvalKind.SELF.name: self_eval,
                    EvalKind.PEER_MANAGER.name: peer_manager_eval,
                    EvalKind.MANAGER_PEER.name: manager_peer_eval,
                    EvalKind.PEER_TO_PEER.name: peer_to_peer_eval,
                }
            })

        return forms

    def generate_eval_reports(self,
                              reviewee,
                              reviewee_evaluations: ReviewerResponse,
                              employee_managers):
        is_add_comenter_to_eval_reports_enabled = super().read_is_add_comenter_to_eval_reports_enabled()
        eval_process_id = super().read_eval_process_id()
        filename_prefix = super().read_google_eval_report_prefix()
        filename = '{}{}'.format(filename_prefix, reviewee)

        company_domain = super().read_company_domain()
        employee_managers = [
            '{}@{}'.format(m, company_domain)
            for m in employee_managers
        ]

        document_id = self.__get_eval_report_id(filename)

        super().insert_eval_report_in_document(
            eval_process_id,
            document_id,
            reviewee,
            reviewee_evaluations)

        if is_add_comenter_to_eval_reports_enabled:
            for email in employee_managers:
                super().create_permission(
                    document_id=document_id,
                    role=GoogleDrive.PERMISSION_ROLE_COMMENTER,
                    email_address=email
                )

        return employee_managers

    def get_peers_assignment(self):
        assignments_peers_range = super().read_assignments_peers_range()

        spreadheet_file = self.__get_assignments_peers_file()
        values = super().get_file_values(
            spreadsheet_id=spreadheet_file.id,
            rows_range=assignments_peers_range)

        # Creating models
        peers = {}
        for row in values:
            if len(row) < 2:
                raise MissingDataException("Missing data in peers, row: %s" % (row))

            reviewer = row[0].strip()
            reviewees = list(map(str.strip, row[1].split(',')))

            peers.update({
                reviewer: reviewees
            })

        return peers

    def write_peers_assignment(self, peers_assignment):
        assignments_peers_range = super().read_assignments_peers_range()

        spreadheet_file = self.__get_assignments_peers_file()

        values = []
        value_input_option = 'RAW'
        for reviewer, peers in peers_assignment.items():
            values.append([reviewer, ','.join(peers)])

        super().update_file_values(
            spreadheet_file.id,
            assignments_peers_range,
            value_input_option,
            values)

    def __get_assignments_peers_file(self):
        google_folder = super().read_google_folder()
        assignments_folder = super().read_assignments_folder()
        assignments_peers_file = super().read_assignments_peers_file()

        file_path = f'/{google_folder}/{assignments_folder}/{assignments_peers_file}'
        return super().gdrive_get_file(file_path)

    def __get_eval_report_id(self, filename):
        '''
            This function returns an ID of an empty eval report document ready to be filled
        '''

        google_folder = super().read_google_folder()
        eval_reports_folder = super().read_eval_reports_folder()

        file_path = f'/{google_folder}/{eval_reports_folder}/{filename}'
        google_file = super().gdrive_get_file(file_path)

        if google_file is None:
            template_id = super().read_google_eval_report_template_id()
            return super().copy_file(template_id, filename)
        else:
            super().empty_document(google_file.id)

        return google_file.id

from evalytics.google_api import GoogleAPI
from evalytics.config import Config
from evalytics.models import GoogleSetup, GoogleFile
from evalytics.models import Employee, EvalKind
from evalytics.exceptions import MissingDataException, NoFormsException

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

    def get_employee_map(self):
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

    def get_forms_map(self):
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

    def get_responses_map(self):
        responses_folder = super().read_google_responses_folder()
        folder = super().get_folder(responses_folder)
        files = super().get_files_from_folder(folder.get('id'))

        number_of_employees = int(super().read_company_number_of_employees())
        responses_range = 'A1:S' + str(number_of_employees + 2)

        responses = {}
        for file in files:
            rows = super().get_file_rows(
                file.get('id'),
                responses_range)

            filename = file.get('name')
            eval_kind = self.__get_eval_kind(filename)

            questions = rows[0][3:]
            for line in rows[1:]:
                reviewer = line[1]
                eval_responses = line[3:]

                eval_responses = list(zip(questions, eval_responses))

                if eval_kind == EvalKind.SELF:
                    reviewee = reviewer
                else:
                    reviewee = line[2]

                eval_response = {
                    'kind': eval_kind.name,
                    'reviewee': reviewee,
                    'eval_response': eval_responses
                }
                if reviewer in responses:
                    acc_responses = responses[reviewer]
                else:
                    acc_responses = []

                acc_responses.append(eval_response)
                responses.update({
                    reviewer: acc_responses
                })

        return responses

    def __get_eval_kind(self, filename):
        if filename.startswith('Manager Evaluation By Team Member'):
            return EvalKind.PEER_MANAGER
        elif filename.startswith('Report Evaluation by Manager'):
            return EvalKind.MANAGER_PEER
        elif filename.startswith('Self Evaluation'):
            return EvalKind.SELF
        else:
            return None

from evalytics.server.api import GoogleAPI
from evalytics.server.config import Config
from evalytics.server.models import GoogleSetup, GoogleFile
from evalytics.server.models import Employee, EvalKind


class Storage:

    def setup(self):
        raise NotImplementedError

    def get_employee_map(self):
        raise NotImplementedError

class GoogleStorage(Storage, GoogleAPI, Config):

    ORGCHART_RANGE = 'A2:C10'
    FORM_MAP_RANGE = 'A2:D3'

    def setup(self):
        folder_name = super().read_google_folder()
        orgchart_filename = super().read_google_orgchart()
        formmap_filename = super().read_google_form_map()

        # Folder setup
        folder = super().get_folder(name=folder_name)
        if folder is None:
            folder = super().create_folder(name=folder_name)

        folder_parent = folder.get('parents')[0]

        # Sheet setup
        files = []
        for filename in [orgchart_filename, formmap_filename]:
            spreadheet_id = super().get_file_id_from_folder(
                folder_id=folder.get('id'),
                filename=filename)

            if spreadheet_id is None:
                spreadheet_id = super().create_spreadhsheet(
                    folder=folder,
                    folder_parent=folder_parent
                )
            files.append(GoogleFile(name=filename, id=spreadheet_id))

        folder = GoogleFile(name=folder_name, id=folder.get('id'))
        return GoogleSetup(
            folder=folder,
            files=files)

    def get_employee_map(self):
        values = super().get_file_rows(
            foldername=super().read_google_folder(),
            filename=super().read_google_orgchart(),
            rows_range=self.ORGCHART_RANGE)

        # Creating models
        employees = {}
        if values:
            for row in values:
                employee_mail = row[0].strip()
                manager = row[1].strip()
                area = row[2].strip()

                employee = Employee(
                    mail=employee_mail,
                    manager=manager,
                    area=area)
                employees.update({employee.uid : employee})

        return employees

    def get_forms_map(self):
        values = super().get_file_rows(
            foldername=super().read_google_folder(),
            filename=super().read_google_form_map(),
            rows_range=self.FORM_MAP_RANGE)

        # Creating models
        forms = {}
        if values:
            for row in values:
                form_area = row[0]
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

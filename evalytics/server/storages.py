from evalytics.server.api import GoogleAPI
from evalytics.server.config import Config
from evalytics.server.models import GoogleSetup, GoogleFile
from evalytics.server.models import Employee, Eval180


class Storage:

    def setup(self):
        raise NotImplementedError

    def get_employee_list(self):
        raise NotImplementedError

class GoogleStorage(Storage, GoogleAPI, Config):

    ORGCHART_RANGE = 'A2:F10'

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

    def get_employee_list(self):
        values = super().get_file_rows(
            foldername=super().read_google_folder(),
            filename=super().read_google_orgchart(),
            rows_range=self.ORGCHART_RANGE)

        # Creating models
        employees = []
        if values:
            for row in values:
                employee_mail = row[0]
                manager = row[1]
                self_eval = row[3]
                manager_eval = row[4]

                eval_180 = Eval180(
                    self_eval=self_eval,
                    manager_eval=manager_eval)
                employee = Employee(
                    mail=employee_mail,
                    manager=manager,
                    eval_180=eval_180)
                employees.append(employee)

        return employees

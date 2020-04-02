from .api import GoogleAPI
from .models import GoogleSetup, GoogleFile
from .models import Employee, Eval180


class Storage:

    def setup(self):
        raise NotImplementedError

    def get_employee_list(self):
        raise NotImplementedError

class GoogleStorage(Storage, GoogleAPI):

    STORAGE_FOLDER_NAME = 'evalytics'
    ORGCHART_NAME = 'orgchart'
    ORGCHART_RANGE = 'A2:F10'

    def setup(self):
        folder_name = self.STORAGE_FOLDER_NAME
        orgchart_filename = self.ORGCHART_NAME

        # Folder setup
        folder = super().get_folder(name=folder_name)
        if folder is None:
            folder = super().create_folder(name=folder_name)

        folder_parent = folder.get('parents')[0]

        # Sheet setup
        spreadheet_id = super().get_file_id_from_folder(
            folder_id=folder.get('id'),
            filename=orgchart_filename)

        if spreadheet_id is None:
            spreadheet_id = super().create_spreadhsheet(
                folder=folder,
                folder_parent=folder_parent
            )

        folder = GoogleFile(name=folder_name, id=folder.get('id'))
        orgchart_file = GoogleFile(name=orgchart_filename, id=spreadheet_id)
        return GoogleSetup(
            folder=folder,
            orgchart_file=orgchart_file,)

    def get_employee_list(self):
        values = super().get_file_rows(
            foldername=self.STORAGE_FOLDER_NAME,
            filename=self.ORGCHART_NAME,
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

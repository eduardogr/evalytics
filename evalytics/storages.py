from evalytics.google_api import GoogleAPI
from evalytics.config import Config
from evalytics.models import GoogleSetup, GoogleFile
from evalytics.models import Employee, EvalKind
from evalytics.models import ReviewerResponse
from evalytics.exceptions import MissingDataException, NoFormsException

class ReviewerResponseBuilder:

    def build(self, questions, filename, eval_kind, line, line_number):
        reviewer = self.__get_reviewer_from_response_line(line)
        reviewee = self.__get_reviewee_from_response_line(
            line, eval_kind)
        eval_response = self.__get_eval_response_from_response_line(
            line, questions)

        return ReviewerResponse(
            reviewee=reviewee,
            reviewer=reviewer,
            eval_kind=eval_kind,
            eval_response=eval_response,
            filename=filename,
            line_number=line_number
        )

    def __get_reviewer_from_response_line(self, line):
        return line[1].split('@')[0]

    def __get_reviewee_from_response_line(self, line, eval_kind):
        if eval_kind == EvalKind.SELF:
            reviewee = self.__get_reviewer_from_response_line(line)
        else:
            reviewee = line[2].strip().lower()

        return reviewee

    def __get_eval_response_from_response_line(self, line, questions):
        eval_responses = line[3:]
        return list(zip(questions, eval_responses))

class ReviewerResponseKeyDictStrategy:

    REVIEWEE_EVALUATION = 'reviewee_evaluation'
    REVIEWER_RESPONSE = 'reviewer_response'

    def get_key(self, data_kind, reviewer_response: ReviewerResponse):

        if self.REVIEWEE_EVALUATION == data_kind:
            return reviewer_response.reviewee

        elif self.REVIEWER_RESPONSE == data_kind:
            return reviewer_response.reviewer

        else:
            raise NotImplementedError('ExtractResponseDataStrategy does not implement %s strategy' % data_kind)

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
        response_kind = ReviewerResponseKeyDictStrategy.REVIEWER_RESPONSE
        return self.__get_reviewer_responses(response_kind)

    def get_evaluations_map(self):
        response_kind = ReviewerResponseKeyDictStrategy.REVIEWEE_EVALUATION
        return self.__get_reviewer_responses(response_kind)

    def generate_eval_reports_in_storage(self,
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

    def __get_reviewer_responses(self, response_kind):
        '''
        return {
            key_1: ReviewerResponse(...),
            ...
            key_N: ReviewerResponse(...),
        }
        '''
        key_strategy = response_kind
        responses = {}
        responses_by_filename = self.__get_responses_by_filename()
        for filename, file_content in responses_by_filename.items():

            questions = file_content['questions']
            file_responses = file_content['responses']
            eval_kind = file_content['eval_kind']

            line_number = 2
            for line in file_responses:

                self.__check_response_line(filename, line)
                reviewer_response = ReviewerResponseBuilder().build(
                    questions,
                    filename,
                    eval_kind,
                    line,
                    line_number,
                )

                key = ReviewerResponseKeyDictStrategy().get_key(
                    key_strategy,
                    reviewer_response
                )

                acc_responses = responses.get(key, [])
                acc_responses.append(reviewer_response)
                responses.update({
                    key: acc_responses
                })

                line_number += 1
            line_number = 2

        return responses

    def __check_response_line(self, filename, line):
        if len(line) < 4:
            raise MissingDataException("Missing data in response file: '%s' in line %s" % (
                filename, line))

    def __get_responses_by_filename(self):
        google_folder = super().read_google_folder()
        responses_folder = super().read_google_responses_folder()

        # TODO: check if folder does not exist
        folder = super().get_folder_from_folder(
            responses_folder,
            google_folder)
        files = super().get_files_from_folder(folder.get('id'))

        number_of_employees = int(super().read_company_number_of_employees())
        responses_range = 'A1:S' + str(number_of_employees + 2)

        responses_by_file = {}
        for file in files:
            filename = file.get('name')
            eval_kind = self.__get_eval_kind(filename)

            if eval_kind is None:
                continue

            rows = super().get_file_rows(
                file.get('id'),
                responses_range)

            if len(rows) < 1:
                raise MissingDataException("Missing data in response file: %s" % (filename))

            questions = rows[0][3:]
            file_responses = rows[1:]

            responses_by_file.update({
                filename: {
                    'questions': questions,
                    'responses': file_responses,
                    'eval_kind': eval_kind,
                }
            })

        return responses_by_file

    def __get_eval_kind(self, filename):
        # TODO: config this
        if filename.startswith('Manager Evaluation By Team Member'):
            return EvalKind.PEER_MANAGER
        elif filename.startswith('Report Evaluation by Manager'):
            return EvalKind.MANAGER_PEER
        elif filename.startswith('Self Evaluation'):
            return EvalKind.SELF
        else:
            return None

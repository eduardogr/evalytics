from evalytics.models import PeersAssignment
from evalytics.models import ReviewerResponse, ReviewerResponseBuilder
from evalytics.mappers import ResponseFileNameToEvalKind
from evalytics.google_api import GoogleAPI
from evalytics.config import Config, ProvidersConfig
from evalytics.exceptions import MissingDataException

class FormsPlatformFactory(Config):

    def get_forms_platform(self):
        forms_platform = super().read_forms_platform_provider()
        if forms_platform == ProvidersConfig.GOOGLE_FORMS:
            return GoogleForms()

        raise ValueError(forms_platform)

class ReviewerResponseKeyDictStrategy:

    REVIEWEE_EVALUATION = 'reviewee_evaluation'
    REVIEWER_RESPONSE = 'reviewer_response'

    def get_key(self, data_kind, reviewer_response: ReviewerResponse):

        if self.REVIEWEE_EVALUATION == data_kind:
            return reviewer_response.reviewee

        elif self.REVIEWER_RESPONSE == data_kind:
            return reviewer_response.reviewer

        else:
            raise NotImplementedError(
                'ReviewerResponseKeyDictStrategy does not implement {} strategy'.format(data_kind))

class GoogleForms(GoogleAPI, ResponseFileNameToEvalKind, Config):

    def get_peers_assignment(self):
        files = self.__get_peers_assignment_response_files()
        return self.__read_peers_assignment(files)

    def get_responses(self):
        response_kind = ReviewerResponseKeyDictStrategy.REVIEWER_RESPONSE
        return self.__get_reviewer_responses(response_kind)

    def get_evaluations(self):
        response_kind = ReviewerResponseKeyDictStrategy.REVIEWEE_EVALUATION
        return self.__get_reviewer_responses(response_kind)

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
            raise MissingDataException(
                "Missing data in response file: '%s' in line %s" % (
                    filename, line))

    def __get_responses_by_filename(self):
        google_folder = super().read_google_folder()
        responses_folder = super().read_google_responses_folder()

        folder_path = f"/{google_folder}/{responses_folder}"
        files = super().googledrive_ls(folder_path)

        # TODO: read responses in batches, read til there's no more responses
        responses_range = 'A1:V' + str(1000)

        responses_by_file = {}
        for file in files:
            eval_kind = super().response_file_name_to_eval_kind(file.name)

            if eval_kind is None:
                continue

            rows = super().get_file_values(
                spreadsheet_id=file.id,
                rows_range=responses_range)

            if len(rows) < 1:
                raise MissingDataException("Missing data in response file: %s" % (file.name))

            questions = rows[0][3:]
            file_responses = rows[1:]

            responses_by_file.update({
                file.name: {
                    'questions': questions,
                    'responses': file_responses,
                    'eval_kind': eval_kind,
                }
            })

        return responses_by_file

    def __get_peers_assignment_response_files(self):
        google_folder = super().read_google_folder()
        assignments_folder = super().read_assignments_folder()
        assignments_manager_forms_folder = super().read_assignments_manager_forms_folder()

        folder_path = f"/{google_folder}/{assignments_folder}/{assignments_manager_forms_folder}"
        return super().googledrive_ls(folder_path)

    def __read_peers_assignment(self, files):
        responses_range = super().read_google_responses_files_range()

        peers_assignment = {}
        unanswered_forms = []

        for file in files:
            rows = super().get_file_values(
                spreadsheet_id=file.id,
                rows_range=responses_range)

            if len(rows) < 1:
                raise MissingDataException("Missing data in response file: %s" % (file.name))

            questions = rows[0]
            reviewees = list(map(self.__get_reviewee_from_question, questions))

            answers = rows[1:]
            if len(answers) == 0:
                unanswered_forms.append(
                    file.name
                )

            for answer in answers:
                assignments = list(zip(reviewees, answer[0:]))
                for assignment in assignments:
                    reviewee = assignment[0]
                    reviewers_assigned = list(map(str.strip, assignment[1].split(',')))

                    for reviewer in reviewers_assigned:
                        reviewees = peers_assignment.get(reviewer, [])
                        if reviewee not in reviewees:
                            reviewees.append(reviewee)
                            peers_assignment.update({
                                reviewer: reviewees
                            })

        return PeersAssignment(peers_assignment, unanswered_forms)

    def __get_reviewee_from_question(self, question):
        '''
            question: Who will review <reviewee>?

            return <reviewee>
        '''
        parts = question.split()
        reviewee = parts[len(parts)-1]
        reviewee = reviewee[:len(reviewee)-1]
        return reviewee

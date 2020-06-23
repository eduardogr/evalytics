from evalytics.models import EvalKind
from evalytics.models import ReviewerResponse, ReviewerResponseBuilder
from evalytics.google_api import GoogleAPI
from evalytics.config import Config, ProvidersConfig
from evalytics.exceptions import MissingDataException
from evalytics.exceptions import MissingGoogleDriveFolderException

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
                'ExtractResponseDataStrategy does not implement {} strategy'.format(data_kind))

class GoogleForms(GoogleAPI, Config):

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

        folder = super().get_folder_from_folder(
            responses_folder,
            google_folder)

        if folder is None:
            raise MissingGoogleDriveFolderException(
                "Missing folder: {}".format(responses_folder))

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

    def __get_peers_assignment_response_files(self):
        google_folder = super().read_google_folder()
        assignments_folder = super().read_assignments_folder()
        assignments_manager_forms_folder = super().read_assignments_manager_forms_folder()

        folder = super().get_folder_from_folder(
            assignments_folder,
            google_folder)

        if folder is None:
            raise MissingGoogleDriveFolderException(
                "Missing folder: {}".format(assignments_folder))

        folder = super().get_folder_from_folder(
            assignments_manager_forms_folder,
            assignments_folder)

        if folder is None:
            raise MissingGoogleDriveFolderException(
                "Missing folder: {}".format(assignments_manager_forms_folder))

        return super().get_files_from_folder(folder.get('id'))

    def __read_peers_assignment(self, files):
        number_of_employees = int(super().read_company_number_of_employees())
        responses_range = 'C1:S' + str(number_of_employees + 2)

        peers_assignment = {}
        for file in files:
            rows = super().get_file_rows(
                file.get('id'),
                responses_range)

            if len(rows) < 1:
                raise MissingDataException("Missing data in response file: %s" % (file.get('name')))

            questions = rows[0][1:]
            reviewees = list(map(self.__get_reviewee_from_question, questions))
            for answer in rows[1:]:
                assignments = list(zip(reviewees, answer[1:]))
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

        return peers_assignment

    def __get_reviewee_from_question(self, question):
        '''
            question: Who will review <reviewee>?

            return <reviewee>
        '''
        parts = question.split()
        reviewee = parts[len(parts)-1]
        reviewee = reviewee[:len(reviewee)-1]
        return reviewee

    def __get_eval_kind(self, filename):
        # TODO: config this
        if filename.startswith('Manager Evaluation By Team Member'):
            return EvalKind.PEER_MANAGER
        elif filename.startswith('Report Evaluation by Manager'):
            return EvalKind.MANAGER_PEER
        elif filename.startswith('Peer Evaluation'):
            return EvalKind.PEER_TO_PEER
        elif filename.startswith('Self Evaluation'):
            return EvalKind.SELF
        else:
            return None

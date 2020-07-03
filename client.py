#!/usr/bin/python3

import json
import sys
import os
import requests

from evalytics.mappers import Mapper

class FileManager:

    def open(self, filename: str, mode: str):
        return open(filename, mode)

class EvalyticsRequests:

    BASE_URL = "http://evalytics:8080"

    def setup(self):
        response = requests.post(
            url="%s/setup" % self.BASE_URL,
            data={})

        return self.__get_data_response(response)

    def reviewers(self):
        response = requests.get(
            url="%s/reviewers" % self.BASE_URL,
            params={})

        return self.__get_data_response(response)

    def status(self):
        response = requests.get(
            url="%s/status" % self.BASE_URL,
            params={})

        return self.__get_data_response(response)

    def communications(self, json_reviewers, kind: str):
        response = requests.post(
            url="%s/communications" % self.BASE_URL,
            data={
                "reviewers": json_reviewers,
                "kind": kind
            }
        )

        return self.__get_data_response(response)

    def evalreports(
            self,
            uids=None,
            managers=None,
            area=None,
            dry_run: bool = False):
        response = requests.post(
            url="%s/evalreports" % self.BASE_URL,
            data={
                "uids": uids,
                "managers": managers,
                "area": area,
                "dry_run": dry_run
            }
        )

        return self.__get_data_response(response)

    def __get_data_response(self, response):
        if response.ok:
            data = response.json()
            data_response = data['response']
            if data['success']:
                return True, data_response
            else:
                return False, data_response
        else:
            return False, response

class EvalyticsClient(EvalyticsRequests, Mapper, FileManager):

    EVALS_NOT_SENT_CSV = 'evals_not_sent.csv'
    EVALS_WHITELIST = 'evals_whitelist.csv'

    def post_setup(self):
        success, response = super().setup()
        return self.__get_response(success, response, 'setup')

    def get_reviewers(self):
        success, response = super().reviewers()
        return self.__get_response(success, response, 'reviewers')

    def get_status(self):
        success, response = super().status()
        return self.__get_response(success, response, 'status')

    def print_reviewers_stats(self, all_reviewers):
        reviewers_by_evals_numbers = {}
        for reviewer in all_reviewers:
            uid = reviewer['employee']['uid']
            evals_number = len(reviewer['evals'])

            if evals_number in reviewers_by_evals_numbers:
                reviewers_by_evals_numbers[evals_number].append(uid)
            else:
                reviewers_by_evals_numbers.update({
                    evals_number: [uid]
                })
        print('\nReviewers per number of evals:')
        for evals_number in sorted(reviewers_by_evals_numbers):
            reviewers = reviewers_by_evals_numbers[evals_number]
            print('  Number of evals: %d' % evals_number)
            print('  Reviewers: %s\n' % reviewers)

    def print_reviewers(self, show_stats: bool = False):
        reviewers = self.get_reviewers()
        for reviewer in reviewers:
            print(json.dumps(reviewer, indent=2))

        if show_stats:
            print('\n-----------')
            print('|  STATS  |')
            print('-----------')
            self.print_reviewers_stats(reviewers)

    def print_status(self):
        status = self.get_status()

        total_evals = 0
        total_completed_evals = 0
        total_pending_evals = 0
        total_inconsistent_evals = 0

        print('\nCompleted evals:')
        for reviewer, completed_evals in status.get('completed', {}).items():
            evals = [uid for uid, e in completed_evals.items()]
            total_completed_evals += len(evals)
            total_evals += len(evals)
            print("  - %s: %s" %(reviewer, evals))

        print('Inconsistent evals:')
        for reviewer, inconsistent_evals in status.get('inconsistent', {}).items():
            evals = [uid for uid, e in inconsistent_evals.items()]
            total_inconsistent_evals += len(evals)
            print("  - %s: %s\n" %(reviewer, evals))

        print('Pending evals:')
        reviewers_with_pending_evals = status.get('pending', '[]')
        reviewers = super().json_to_reviewers(reviewers_with_pending_evals)
        for uid, reviewer in reviewers.items():
            total_pending_evals += len(reviewer.evals)
            total_evals += len(reviewer.evals)
            print("  - %s: %s" %(uid, [e.reviewee for e in reviewer.evals]))

        print("\nTotal evals: {}".format(total_evals))
        if total_evals > 0:
            pending_percentage = total_pending_evals / total_evals * 100
            completed_percentage = total_completed_evals / total_evals * 100
            print("Completed evals: {0:.2f} % ({1:.0f})".format(
                completed_percentage,
                total_completed_evals))
            print("Pending evals: {0:.2f} % ({1:.0f})".format(
                pending_percentage,
                total_pending_evals))
            print("Inconsitent evals: %s" % total_inconsistent_evals)

    def print_inconsistent_files_status(self):
        status = self.get_status()

        inconsistent_files = {}

        print('\nInconsistent evals:')
        for reviewer, inconsistent_evals in status.get('inconsistent', {}).items():
            evals = []
            for uid, evaluation in inconsistent_evals.items():
                evals.append(uid)
                filename = evaluation['filename']
                reasons = inconsistent_files.get(filename, [])
                reasons.append({
                    'reason': evaluation['reason'],
                    'line': evaluation['line_number']
                })
                inconsistent_files.update({
                    filename: reasons
                })

            print("  - %s: %s\n" %(reviewer, evals))

        print('Inconsistent files:')
        for filename, reasons in inconsistent_files.items():
            print("  - File: '%s'" % filename)
            for reason in reasons:
                print('    - (Line %s) %s' % (reason['line'], reason['reason']))
            print()

    def send_communication(self, kind, reviewers, whitelist=None, dry_run: bool = False):
        if whitelist is not None:
            reviewers = [reviewer
                         for r_uid, reviewer in reviewers.items()
                         if r_uid in whitelist]
        else:
            reviewers = [reviewer for r_uid, reviewer in reviewers.items()]

        self.__send_communication(reviewers, kind, dry_run)

    def generate_reports(self, dry_run, whitelist=None):
        uids = super().list_to_json(whitelist)
        success, response = super().evalreports(
            dry_run=dry_run,
            uids=uids)

        if success:
            evals_reports = response['evals_reports']
            created = evals_reports['created']
            not_created = evals_reports['not_created']

            print('[DRY-RUN] %s' % dry_run)
            print("Reports created:")
            for uid, reports_created in created.items():
                print(' - {} report will be shared with {}'.format(uid, reports_created['managers']))

            print("Reports NOT created: %s" % not_created)
            for uid, reports_not_created in not_created.items():
                print(' - {} report will be shared with {}'.format(uid, reports_not_created['managers']))

    def get_whitelist(self):
        return self.__get_list_from(self.EVALS_WHITELIST)

    def get_retry_list(self):
        return self.__get_list_from(self.EVALS_NOT_SENT_CSV)

    def help(self, command):
        help_message = {
            'Message': "Command '{}' not expected".format(command),
            'Available commands: [OPTIONS]': {
                'setup': [],
                'reviewers': ['--stats'],
                'send_evals': ['--retry', '--whitelist', '--dry-run'],
                'send_due_date_comm': ['--retry', '--whitelist', '--dry-run'],
                'send_reminders': ['--retry', '--whitelist', '--dry-run'],
                'status': ['--inconsisten-files'],
                'reports': ['--whitelist', '--dry-run'],
            }
        }
        print(json.dumps(help_message))

    def __get_response(self, success, response, key):
        if success:
            return response[key]
        else:
            if 'error' in response:
                print("[Controlled Error] %s" % response['error'])
            else:
                print("[ERROR] Something failed. key: {}".format(key))
                print("  - HTTP code: %s" % response.status_code)
                print("  - Error response: %s" % response.content)
            return {}

    def __get_list_from(self, filename):
        list_from_file = []
        list_file = super().open(filename, "r")
        for reviewer in list_file.readlines():
            list_from_file.append(reviewer.strip())
        list_file.close()

        return list_from_file

    def __send_communication(self, reviewers, kind: str, dry_run: bool):
        json_reviewers = super().reviewer_to_json_object(reviewers)

        if dry_run:
            for reviewer in reviewers:
                print('[DRY-RUN] Reviewer %s has %d evals' % (reviewer.uid, len(reviewer.evals)))
        else:
            success, response = super().communications(json_reviewers, kind)
            if success:
                print("Evals sent: %s" % response['comms_sent'])
                print("Evals NOT sent: %s" % response['comms_not_sent'])

                comms_not_sent = response['comms_not_sent']
                if len(comms_not_sent) > 0:
                    evals_not_sent_file = open(self.EVALS_NOT_SENT_CSV, "w+")
                    for reviewer in comms_not_sent:
                        evals_not_sent_file.write("%s\n" % reviewer)
                    evals_not_sent_file.close()
                else:
                    if os.path.exists(self.EVALS_NOT_SENT_CSV):
                        os.remove(self.EVALS_NOT_SENT_CSV)

            else:
                print("[ERROR] Something failed sending emails")
                print("  - Error response: {}".format(response['error']))

class CommandFactory(EvalyticsClient):

    SETUP = 'setup'
    REVIEWERS = 'reviewers'
    SEND_EVALS = 'send_evals'
    SEND_DUE_DATE_COMM = 'send_due_date_comm'
    SEND_REMIDERS = 'send_reminders'
    STATUS = 'status'
    REPORTS = 'reports'

    def execute(self, args):

        command = args.pop(0)
        dry_run = '--dry-run' in args
        with_retry = '--retry' in args
        with_whitelist = '--whitelist' in args

        whitelist = None
        retry_list = None

        if dry_run:
            args.remove('--dry-run')

        if with_retry:
            args.remove('--retry')
            retry_list = super().get_retry_list()

        if with_whitelist:
            args.remove('--whitelist')
            whitelist = super().get_whitelist()

        if command == CommandFactory.SETUP:
            super().post_setup()

        elif command == CommandFactory.REVIEWERS:
            show_stats = '--stats' in args
            super().print_reviewers(show_stats=show_stats)

        elif command in [
                CommandFactory.SEND_EVALS,
                CommandFactory.SEND_DUE_DATE_COMM,
                CommandFactory.SEND_REMIDERS]:
            command_to_kind = {
                'send_evals': 'process_started',
                'send_due_date_comm': 'due_date_reminder',
                'send_reminders': 'pending_evals_reminder'
            }
            kind = command_to_kind.get(command)

            reviewers = self.__get_reviewers(kind)
            reviewers = super().json_to_reviewers(reviewers)

            if with_retry:
                whitelist = retry_list

            super().send_communication(
                    kind=kind,
                    reviewers=reviewers,
                    dry_run=dry_run,
                    whitelist=whitelist)

        elif command == CommandFactory.STATUS:
            if '--inconsistent-files' in args:
                super().print_inconsistent_files_status()
            else:
                super().print_status()

        elif command == CommandFactory.REPORTS:
            super().generate_reports(
                dry_run=dry_run,
                whitelist=whitelist)
        else:
            super().help(command)

    def __get_reviewers(self, kind):
        if kind == 'process_started':
            reviewers = self.get_reviewers()
        elif kind in ['due_date_reminder', 'pending_evals_reminder']:
            status = self.get_status()
            reviewers = status.get('pending', '[]')
        else:
            raise ValueError(kind)

        return reviewers

if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise Exception("No arguments given")

    CommandFactory().execute(sys.argv[1:])

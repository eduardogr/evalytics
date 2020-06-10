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

    def evaldelivery(self, json_reviewers, is_reminder: bool = False):
        response = requests.post(
            url="%s/evaldelivery" % self.BASE_URL,
            data={
                "reviewers": json_reviewers,
                "is_reminder": is_reminder
            }
        )

        return self.__get_data_response(response)

    def evalreports(
            self,
            eval_process_id: str,
            uids=None,
            managers=None,
            area=None,
            dry_run: bool = False):
        response = requests.post(
            url="%s/evalreports" % self.BASE_URL,
            data={
                "eval_process_id": eval_process_id,
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
        if success:
            setup = response['setup']
            print(json.dumps(setup, indent=2))
            return setup
        else:
            if 'error' in response:
                print("[Controlled Error] %s" % response['error'])
            else:
                print("[ERROR] Something failed in get reviewers")
                print("  - HTTP code: %s" % response.status_code)
                print("  - Error response: %s" % response.content)
            return []

    def get_reviewers(self):
        success, response = super().reviewers()
        if success:
            return response['reviewers']
        else:
            if 'error' in response:
                print("[Controlled Error] %s" % response['error'])
            else:
                print("[ERROR] Something failed in get reviewers")
                print("  - HTTP code: %s" % response.status_code)
                print("  - Error response: %s" % response.content)
            return []

    def get_status(self):
        success, response = super().status()
        if success:
            return response['status']
        else:
            if 'error' in response:
                print("[Controlled Error] %s" % response['error'])
            else:
                print("[ERROR] Something failed in get reviewers")
                print("  - HTTP code: %s" % response.status_code)
                print("  - Error response: %s" % response.content)
            return []

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

    def send_eval(self, whitelist=None, dry_run: bool = False):
        response_reviewers = self.get_reviewers()
        reviewers = super().json_to_reviewers(response_reviewers)

        if whitelist is not None:
            reviewers = [reviewer
                         for r_uid, reviewer in reviewers.items()
                         if r_uid in whitelist]
        else:
            reviewers = [reviewer for r_uid, reviewer in reviewers.items()]

        is_reminder = False
        self.__eval_delivery(reviewers, is_reminder, dry_run)

    def retry_send_eval(self, dry_run: bool = False):
        evals_not_sent = []
        evals_not_sent_file = super().open(self.EVALS_NOT_SENT_CSV, "r")
        for reviewer in evals_not_sent_file.readlines():
            evals_not_sent.append(reviewer.strip())
        evals_not_sent_file.close()
        self.send_eval(whitelist=evals_not_sent, dry_run=dry_run)

    def whitelist_send_eval(self, dry_run: bool = False):
        whitelisted_evals = []
        whitelisted_evals_file = super().open(self.EVALS_WHITELIST, "r")
        for reviewer in whitelisted_evals_file.readlines():
            whitelisted_evals.append(reviewer.strip())
        whitelisted_evals_file.close()
        self.send_eval(whitelist=whitelisted_evals, dry_run=dry_run)

    def send_reminder(self, whitelist=None, dry_run: bool = False):
        status = self.get_status()
        reviewers_with_pending_evals = status.get('pending', '[]')
        reviewers = super().json_to_reviewers(reviewers_with_pending_evals)

        if whitelist is not None:
            reviewers = [reviewer
                         for r_uid, reviewer in reviewers.items()
                         if r_uid in whitelist]
        else:
            reviewers = [reviewer for r_uid, reviewer in reviewers.items()]

        is_reminder = True
        self.__eval_delivery(reviewers, is_reminder, dry_run)

    def retry_send_reminder(self, dry_run: bool = False):
        evals_not_sent = []
        evals_not_sent_file = super().open(self.EVALS_NOT_SENT_CSV, "r")
        for reviewer in evals_not_sent_file.readlines():
            evals_not_sent.append(reviewer.strip())
        evals_not_sent_file.close()
        self.send_reminder(whitelist=evals_not_sent, dry_run=dry_run)

    def whitelist_send_reminder(self, dry_run: bool = False):
        whitelisted_evals = []
        whitelisted_evals_file = super().open(self.EVALS_WHITELIST, "r")
        for reviewer in whitelisted_evals_file.readlines():
            whitelisted_evals.append(reviewer.strip())
        whitelisted_evals_file.close()
        self.send_reminder(whitelist=whitelisted_evals, dry_run=dry_run)

    def generate_reports(self, eval_process_id, dry_run, employee_uids = None):
        uids = super().list_to_json(employee_uids)
        success, response = super().evalreports(
            eval_process_id=eval_process_id,
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

    def whitelist_generate_reports(self, eval_process_id, dry_run):
        whitelisted_evals = []
        whitelisted_evals_file = super().open(self.EVALS_WHITELIST, "r")
        for reviewer in whitelisted_evals_file.readlines():
            whitelisted_evals.append(reviewer.strip())
        whitelisted_evals_file.close()
        self.generate_reports(eval_process_id=eval_process_id, dry_run=dry_run, employee_uids=whitelisted_evals)

    def __eval_delivery(self, reviewers, is_reminder: bool, dry_run: bool):
        json_reviewers = super().reviewer_to_json(reviewers)

        if dry_run:
            for reviewer in reviewers:
                print('[DRY-RUN] Reviewer %s has %d evals' % (reviewer.uid, len(reviewer.evals)))
        else:
            success, response = super().evaldelivery(json_reviewers, is_reminder)
            if success:
                print("Evals sent: %s" % response['evals_sent'])
                print("Evals NOT sent: %s" % response['evals_not_sent'])

                evals_not_sent = response['evals_not_sent']
                if len(evals_not_sent) > 0:
                    evals_not_sent_file = open(self.EVALS_NOT_SENT_CSV, "w+")
                    for reviewer in evals_not_sent:
                        evals_not_sent_file.write("%s\n" % reviewer)
                    evals_not_sent_file.close()
                else:
                    if os.path.exists(self.EVALS_NOT_SENT_CSV):
                        os.remove(self.EVALS_NOT_SENT_CSV)

            else:
                print("[ERROR] Something failed sending emails")
                print("  - HTTP code: %s" % response.status_code)
                print("  - Error response: %s" % response.content)

    def help(self, command):
        print("Command '%s' not expected" % command)
        print("Available commands: ")
        print("  - %s" % 'setup')

        print("  - %s" % 'reviewers')
        print("  - %s --stats" % 'reviewers')

        print("  - %s" % 'send_evals')
        print("  - %s --retry" % 'send_evals')
        print("  - %s --whitelist" % 'send_evals')
        print("  - %s --dry-run" % 'send_evals')

        print("  - %s" % 'send_reminders')
        print("  - %s --retry" % 'send_reminders')
        print("  - %s --whitelist" % 'send_reminders')
        print("  - %s --dry-run" % 'send_reminders')

        print("  - %s" % 'status')
        print("  - %s --inconsistent-files" % 'status')

class CommandFactory(EvalyticsClient):
    def execute(self, args):

        command = args.pop(0)
        dry_run = '--dry-run' in args
        with_retry = '--retry' in args
        with_whitelist = '--whitelist' in args

        if dry_run:
            args.remove('--dry-run')
        if with_retry:
            args.remove('--retry')
        if with_whitelist:
            args.remove('--whitelist')

        eval_process_id = 'Default eval id'
        for arg in args:
            arg_with_value = arg.split('=')
            if arg_with_value[0] == '--eval-process-id':
                eval_process_id = arg_with_value[1]

        if command == 'setup':
            super().post_setup()

        elif command == 'reviewers':
            show_stats = '--stats' in args
            super().print_reviewers(show_stats=show_stats)

        elif command == 'send_evals':

            if with_retry:
                super().retry_send_eval(dry_run=dry_run)
            elif with_whitelist:
                super().whitelist_send_eval(dry_run=dry_run)
            else:
                super().send_eval(dry_run=dry_run)

        elif command == 'send_reminders':

            if with_retry:
                super().retry_send_reminder(dry_run=dry_run)
            elif with_whitelist:
                super().whitelist_send_reminder(dry_run=dry_run)
            else:
                super().send_reminder(dry_run=dry_run)

        elif command == 'status':
            if '--inconsistent-files' in args:
                super().print_inconsistent_files_status()
            else:
                super().print_status()

        elif command == 'reports':

            if with_whitelist:
                super().whitelist_generate_reports(
                    eval_process_id=eval_process_id,
                    dry_run=dry_run)
            else:
                super().generate_reports(
                    eval_process_id=eval_process_id,
                    dry_run=dry_run)
        else:
            super().help(command)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise Exception("No arguments given")

    CommandFactory().execute(sys.argv[1:])

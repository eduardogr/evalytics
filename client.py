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

    def sendmail(self, json_reviewers):
        response = requests.post(
            url="%s/sendmail" % self.BASE_URL,
            data={
                "reviewers": json_reviewers
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
    EVALS_WHITELISTED = 'evals_whitelisted.csv'

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

        print('Completed evals:')
        for reviewer, completed_evals in status.get('completed', {}).items():
            evals = [uid for uid, e in completed_evals.items()]
            total_completed_evals += len(evals)
            total_evals += len(evals)
            print("  - %s: %s" %(reviewer, evals))

        print('Pending evals:')
        for reviewer, pending_evals in status.get('pending', {}).items():
            evals = [uid for uid, e in pending_evals.items()]
            total_pending_evals += len(evals)
            total_evals += len(evals)
            print("  - %s: %s" %(reviewer, evals))

        print('Inconsistent evals:')
        for reviewer, inconsistent_evals in status.get('inconsistent', {}).items():
            evals = [uid for uid, e in inconsistent_evals.items()]
            total_inconsistent_evals += len(evals)
            total_evals += len(evals)
            print("  - %s: %s\n" %(reviewer, evals))

        pending_percentage = total_pending_evals / total_evals * 100
        completed_percentage = total_completed_evals / total_evals * 100

        print("Total evals: {}".format(total_evals))
        print("Completed evals: {0:.2f} % ({1:.0f})".format(
            completed_percentage,
            total_completed_evals))
        print("Pending evals: {0:.2f} % ({1:.0f})".format(
            pending_percentage,
            total_pending_evals))
        print("Inconsitent evals: %s" % total_inconsistent_evals)

    def send_eval(self, whitelist=None, dry_run: bool = False):
        response_reviewers = self.get_reviewers()
        reviewers = super().json_to_reviewers(response_reviewers)

        if whitelist is not None:
            reviewers = [reviewer
                         for r_uid, reviewer in reviewers.items()
                         if r_uid in whitelist]
        else:
            reviewers = [reviewer for r_uid, reviewer in reviewers.items()]

        json_reviewers = super().reviewer_to_json(reviewers)

        if dry_run:
            for reviewer in reviewers:
                print('[DRY-RUN] Reviewer %s has %d evals' % (reviewer.uid, len(reviewer.evals)))
        else:
            success, response = super().sendmail(json_reviewers)
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

    def retry_send_eval(self, dry_run: bool = False):
        evals_not_sent = []
        evals_not_sent_file = super().open(self.EVALS_NOT_SENT_CSV, "r")
        for reviewer in evals_not_sent_file.readlines():
            evals_not_sent.append(reviewer.strip())
        evals_not_sent_file.close()
        self.send_eval(whitelist=evals_not_sent, dry_run=dry_run)

    def whitelist_send_eval(self, dry_run: bool = False):
        whitelisted_evals = []
        whitelisted_evals_file = super().open(self.EVALS_WHITELISTED, "r")
        for reviewer in whitelisted_evals_file.readlines():
            whitelisted_evals.append(reviewer.strip())
        whitelisted_evals_file.close()
        self.send_eval(whitelist=whitelisted_evals, dry_run=dry_run)

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
        print("  - %s" % 'status')

class CommandFactory(EvalyticsClient):
    def execute(self, command):
        args = command.split(' ')
        if 'setup' in args:
            super().post_setup()

        elif 'reviewers' in args:
            show_stats = '--stats' in args
            super().print_reviewers(show_stats=show_stats)

        elif 'send_evals' in args:
            dry_run = '--dry-run' in args

            if '--retry' in args:
                super().retry_send_eval(dry_run=dry_run)
            elif '--whitelist' in args:
                super().whitelist_send_eval(dry_run=dry_run)
            else:
                super().send_eval(dry_run=dry_run)
        elif 'status' in args:
            super().print_status()
        else:
            super().help(command)

if __name__ == "__main__":
    command_arg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    CommandFactory().execute(command_arg)

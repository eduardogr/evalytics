#!/usr/bin/python3

import json
import sys
import os
import requests

from evalytics.server.mappers import Mapper

class EvalyticsRequests:

    BASE_URL = "http://localhost:8080"

    def setup(self):
        response = requests.post(
            url="%s/setup" % self.BASE_URL,
            data={})

        return self.get_data_response(response)

    def reviewers(self):
        response = requests.get(
            url="%s/reviewers" % self.BASE_URL,
            params={})

        return self.get_data_response(response)

    def sendmail(self, json_reviewers):
        response = requests.post(
            url="%s/sendmail" % self.BASE_URL,
            data={
                "reviewers": json_reviewers
            }
        )

        return self.get_data_response(response)

    def get_data_response(self, response):
        if response.ok:
            data = response.json()
            data_response = data['response']
            if data['success']:
                return True, data_response
            else:
                return False, data_response
        else:
            return False, response

class EvalyticsClient(EvalyticsRequests, Mapper):

    EVALS_NOT_SENT_CSV = 'evals_not_sent.csv'

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

    def get_reviewers_stats(self):
        all_reviewers = self.get_reviewers()
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
        for evals_number in sorted(reviewers_by_evals_numbers):
            reviewers = reviewers_by_evals_numbers[evals_number]
            print('Number of evals: %d' % evals_number)
            print('Reviewers: %s' % reviewers)


    def print_reviewers(self):
        for reviewer in self.get_reviewers():
            print(json.dumps(reviewer, indent=2))

    def send_eval(self, whitelist=None):
        response_reviewers = self.get_reviewers()
        reviewers = super().json_to_reviewer(response_reviewers)

        if whitelist is not None:
            reviewers = [reviewer
                         for r_uid, reviewer in reviewers.items()
                         if r_uid in whitelist]
        else:
            reviewers = [reviewer for r_uid, reviewer in reviewers.items()]

        json_reviewers = super().reviewer_to_json(reviewers)

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

    def retry_send_eval(self):
        evals_not_sent = []
        evals_not_sent_file = open(self.EVALS_NOT_SENT_CSV, "r")
        for reviewer in evals_not_sent_file.readlines():
            evals_not_sent.append(reviewer.strip())
        evals_not_sent_file.close()
        self.send_eval(whitelist=evals_not_sent)

    def help(self, command):
        print("Command '%s' not expected" % command)
        print("Available commands: ")
        print("  - %s" % " ".join('post_setup'.split('_')))
        print("  - %s" % " ".join('get_reviewers'.split('_')))
        print("  - %s" % " ".join('send_evals'.split('_')))

class CommandFactory(EvalyticsClient):
    def execute(self, command):
        if command == 'post setup':
            super().post_setup()
        elif command == 'get reviewers':
            super().print_reviewers()
        elif command == 'get reviewers --stats':
            super().get_reviewers_stats()
        elif command == 'send evals':
            super().send_eval()
        elif command == 'send evals --retry':
            super().retry_send_eval()
        else:
            super().help(command)

if __name__ == "__main__":
    command_arg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    CommandFactory().execute(command_arg)

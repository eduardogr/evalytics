#!/usr/bin/python3

import json
import sys
import requests

from evalytics.server.mappers import Mapper

class EvalyticsClient(Mapper):

    BASE_URL = "http://localhost:8080"

    def get_reviewers(self):
        response = requests.get(
            url="%s/reviewers" % self.BASE_URL,
            params={})

        success, response = self.get_data_response(response)
        if success:
            return response['reviewers']
        else:
            print("Something failed")
            print(response)
            print(response.__dict__)
            return []

    def print_reviewers(self):
        for reviewer in self.get_reviewers():
            print(json.dumps(reviewer, indent=2))

    def send_eval(self):
        response_reviewers = self.get_reviewers()
        reviewers = super().json_to_reviewer(response_reviewers)
        reviewers = [reviewer for r_uid, reviewer in reviewers.items()]

        json_reviewers = super().reviewer_to_json(reviewers)

        response = requests.post(
            url="%s/sendmail" % self.BASE_URL,
            data={
                "reviewers": json_reviewers
            }
        )

        success, response = self.get_data_response(response)
        if success:
            print("Evals sent: %s" % response['evals_sent'])
            print("Evals NOT sent: %s" % response['evals_not_sent'])
        else:
            print("Something failed")
            print(response)
            print(response.__dict__)

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

class CommandFactory(EvalyticsClient):
    def execute(self, command):
        if command == 'print_reviewers':
            super().print_reviewers()
        elif command == 'sendmail':
            super().send_eval()
        else:
            print("Command '%s' not expected" % command)
            print("Available commands: ")
            print("  - print_reviewers")
            print("  - sendmail")

if __name__ == "__main__":
    command_arg = sys.argv[1] if len(sys.argv) > 1 else ""
    CommandFactory().execute(command_arg)

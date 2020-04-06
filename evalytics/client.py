#!/usr/bin/python3

import json
import sys
import requests

from evalytics.server.mappers import Mapper
from evalytics.server.models import Reviewer, Employee, Eval, EvalKind


class EvalyticsClient(Mapper):

    BASE_URL = "http://localhost:8080"

    def get_reviewers(self):
        response = requests.get(
            url="%s/reviewers" % self.BASE_URL,
            params={})

        data = response.json()
        return data['reviewers']

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

        if response.ok:
            data = response.json()
            for r in data['reviewers']:
                print(json.dumps(r, indent=2))
        else:
            print(response)
            print(response.__dict__)

class CommandFactory(EvalyticsClient):
    def execute(self, command):
        if command == 'print_reviewers':
            super().print_reviewers()
        elif command == 'sendmail':
            super().send_eval()
        else:
            print("Command '%s' not expected" % command)

if __name__ == "__main__":
    CommandFactory().execute(sys.argv[1])

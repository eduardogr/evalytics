#!/usr/bin/python3

import json
import sys
import requests

from evalytics.server.models import Reviewer, Employee, Eval, EvalKind

BASE_URL = "http://localhost:8080"

# extracting data in json format

def get_reviewers():
    response = requests.get(
        url="%s/reviewers" % BASE_URL,
        params={})

    data = response.json()
    return data['reviewers']

def print_reviewers():
    for reviewer in get_reviewers():
        print(json.dumps(reviewer, indent=2))

def send_eval():
    response_reviewers = get_reviewers()
    reviewers = []
    for r in response_reviewers:
        r_employee = r['employee']
        employee = Employee(
            mail=r_employee['mail'],
            manager=r_employee['manager'],
            area=r_employee['area'],
        )
        evals = []
        for e in r['evals']:
            evals.append(
                Eval(
                    reviewee=e['reviewee'],
                    kind=EvalKind.from_str(e['kind']),
                    form=e['form'],
                ))
        reviewer = Reviewer(
            employee=employee,
            evals=evals
        )
        reviewers.append(reviewer)

    json_reviewers = json.dumps(
        reviewers,
        default=lambda o: o.__dict__ if type(o) is not EvalKind else str(o.name))

    response = requests.post(
        url="%s/sendmail" % BASE_URL,
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


def command_factory(command):
    if command == 'print_reviewers':
        print_reviewers()
    elif command == 'sendmail':
        send_eval()
    else:
        print("Command '%s' not expected" % command)


if __name__ == "__main__":
    command_factory(sys.argv[1])

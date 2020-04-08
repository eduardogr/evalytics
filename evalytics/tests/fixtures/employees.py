# pylint: disable=invalid-name
# No need to shout here

from evalytics.server.models import Employee

def employees_collection():
    return {
        'em_email': Employee(
            mail='em_email@email.com',
            manager='mymanager',
            area=None),
        'manager_em': Employee(
            mail='manager_em@email.com',
            manager='cto',
            area=None),
    }

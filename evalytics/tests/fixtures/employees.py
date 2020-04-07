# pylint: disable=invalid-name
# No need to shout here

from evalytics.server.models import EmployeeNode, Employee

jane = EmployeeNode(employee=Employee(
        mail='jane@tuenti.com',
        manager='',
        area=None))
jhon = EmployeeNode(employee=Employee(
        mail='jhon@tuenti.com',
        manager='jane',
        area=None
    ), supervisor=jane)
minion_1 = EmployeeNode(employee=Employee(
        mail='minion1@tuenti.com',
        manager='jhon',
        area=None
    ), supervisor=jhon)
minion_2 = EmployeeNode(employee=Employee(
        mail='minion2@tuenti.com',
        manager='jhon',
        area=None
    ), supervisor=jhon)
minion_3 = EmployeeNode(employee=Employee(
        mail='minion3@tuenti.com',
        manager='jhon',
        area=None
    ), supervisor=jhon)

def employee_nodes():
    return {
        'jane': jane,
        'jhon': jhon,
        'minion_1': minion_1,
        'minion_2': minion_2,
        'minion_3': minion_3
    }

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

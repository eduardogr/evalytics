# pylint: disable=invalid-name
# No need to shout here

from evalytics.server.models import EmployeeNode, Employee

jane = EmployeeNode(employee=Employee(
        name='Jane of hte jungle',
        mail='jane@tuenti.com'))
jhon = EmployeeNode(employee=Employee(
        name='John Ahtelstan',
        mail='jhon@tuenti.com'
    ), supervisor=jane)
minion_1 = EmployeeNode(employee=Employee(
        name='Minion the First',
        mail='minion1@tuenti.com'
    ), supervisor=jhon)
minion_2 = EmployeeNode(employee=Employee(
        name='Minion the Second',
        mail='minion2@tuenti.com'
    ), supervisor=jhon)
minion_3 = EmployeeNode(employee=Employee(
        name='Minion The Third',
        mail='minion3@tuenti.com'
    ), supervisor=jhon)

def employee_nodes():
    return {
        'jane': jane,
        'jhon': jhon,
        'minion_1': minion_1,
        'minion_2': minion_2,
        'minion_3': minion_3
    }

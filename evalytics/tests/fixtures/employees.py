# pylint: disable=invalid-name
# No need to shout here

from evalytics.server.models import Employee

jane = Employee('jane@tuenti.com')
jhon = Employee('jhon@tuenti.com', supervisor=jane)
minion_1 = Employee('minion1@tuenti.com', supervisor=jhon)
minion_2 = Employee('minion2@tuenti.com', supervisor=jhon)
minion_3 = Employee('minion3@tuenti.com', supervisor=jhon)

from .models import EvalKind, Eval, Reviewer, Employee
from .config import Config
from .exceptions import MissingDataException

class EmployeeAdapter(Config):

    def get_employees_by_manager(self, employees):
        managers = {
            employees[e.manager].uid:[]
            for uid, e in employees.items() if e.has_manager and e.manager in employees}

        for _, e in employees.items():
            if e.manager and e.manager in employees:
                managers[e.manager].append(e.uid)

        return managers

    def build_reviewers(self, employees, forms):
        employees_by_manager = self.get_employees_by_manager(employees)

        reviewers = {}
        for uid, employee in employees.items():
            evals = []

            if employee.area not in forms:
                raise MissingDataException("Missing area '%s' in forms" % employee.area)

            employee_forms = forms[employee.area]

            evals.append(Eval(
                reviewee=uid,
                kind=EvalKind.SELF,
                form=employee_forms[EvalKind.SELF]))

            if employee.has_manager:
                evals.append(Eval(
                    reviewee=employee.manager,
                    kind=EvalKind.PEER_MANAGER,
                    form=employee_forms[EvalKind.PEER_MANAGER]))

                # Employee's manager has no manager, no PEER_MANAGER evaluation
                # Employee's manager has no SELF evaluation
                if employee.manager not in employees_by_manager:
                    manager_peer_eval = Eval(
                        reviewee=employee.uid,
                        kind=EvalKind.MANAGER_PEER,
                        form=employee_forms[EvalKind.MANAGER_PEER])

                    if employee.manager in reviewers:
                        reviewer_manager = reviewers[employee.manager]
                        reviewer_manager.evals.append(manager_peer_eval)
                    else:
                        manager = Employee(
                            mail=employee.manager + '@' + super().read_company_domain(),
                            manager='',
                            area=employee.area) # Manager has the same area
                        reviewer_manager = Reviewer(
                            employee=manager,
                            evals=[
                                manager_peer_eval
                            ]
                        )
                    reviewers.update({
                            manager.uid: reviewer_manager
                        })

            # Employee is a manager
            if uid in employees_by_manager:
                for employee_uid in employees_by_manager[uid]:
                    evals.append(Eval(
                        reviewee=employee_uid,
                        kind=EvalKind.MANAGER_PEER,
                        form=employee_forms[EvalKind.MANAGER_PEER]))

            reviewer = Reviewer(
                employee=employee,
                evals=evals
            )
            reviewers.update({reviewer.uid: reviewer})

        return reviewers

    def build_eval_message(self, reviewer: Reviewer):
        list_of_evals = ''
        for e_eval in reviewer.evals:
            if e_eval.kind is EvalKind.SELF:
                reviewee = 'Your self review'
            else:
                reviewee = e_eval.reviewee

            list_of_evals = list_of_evals + \
                    '<a href="' + e_eval.form \
                    + '" style="color:#0ADA7C;display:block;margin:5px 0" target="_blank"><b>'\
                    + reviewee + '</b></a>'

        return '''<div><table style="font-family:HelveticaNeue-Light,Helvetica Neue Light,Helvetica Neue,Helvetica,Arial,Lucida Grande,sans-serif;text-align:center;color:#F6F6F6;font-size:15px" width="100%" cellspacing="0" cellpadding="0" border="0" bgcolor="#EEEEEE">
	<tbody><tr height="60" bgcolor="#000000;"><td style="text-align:left"></td></tr><tr><td>
			<table style="max-width:615px;padding:30px 7% 30px;border-bottom:2px solid #EEEEEE;border-radius:5px;text-align:center" width="100%" cellspacing="0" cellpadding="0" border="0" bgcolor="#fff" align="center">
			<tbody><tr><td><h1 style="font-size:25px;font-weight:normal;letter-spacing:-1px;color:#757575;padding:0 0 10px">
            Hi {0},</h1>
            <b></b><p style="color:#757575;line-height:23px;padding:30px auto">
                You have new assignments !	
            </b></p></td>
            </tr>
            <tr><td style="padding:10px 0">
                    {1}
            </td></tr></tbody></tr></table></div>'''.format(reviewer.uid, list_of_evals)

class ReviewerAdapter(EmployeeAdapter):

    def get_status_from_responses(self, reviewers, responses):
        completed = {}
        pending = {}
        inconsistent = {}

        employees = {r.uid:r.employee for uid, r in reviewers.items()}
        employees_by_manager = super().get_employees_by_manager(employees)

        for uid, responses in responses.items():
            completed_responses = {}
            inconsistent_responses = {}
            for response in responses:
                if uid not in reviewers:
                    continue

                reviewer = reviewers[uid]
                reason = self.__get_reason_of_inconsistent_response(
                    reviewer,
                    response,
                    employees_by_manager
                )

                if reason is None:
                    completed_responses.update({
                        response['reviewee']: {
                            'kind': response['kind'],
                        }
                    })
                else:
                    inconsistent_responses.update({
                        response['reviewee']: {
                            'kind': response['kind'],
                            'reason': reason
                        }
                    })
            if len(completed_responses) > 0:
                completed.update({
                    uid: completed_responses
                })
            if len(inconsistent_responses) > 0:
                inconsistent.update({
                    uid: inconsistent_responses
                })

        for uid, reviewer in reviewers.items():
            evals = reviewer.evals
            pending_responses = {}
            for e in evals:
                if e.reviewee not in completed.get(uid, {}):
                    pending_responses.update({
                        e.reviewee: {
                            'kind': e.kind.name,
                            'form': e.form
                        }
                    })
            if len(pending_responses) > 0:
                pending.update({
                    uid: pending_responses
                })

        return completed, pending, inconsistent

    def __get_reason_of_inconsistent_response(self,
                                              reviewer,
                                              response,
                                              employees_by_manager):
        reason = None
        if response['kind'] == EvalKind.PEER_MANAGER.name:
            if reviewer.employee.manager != response['reviewee']:
                reason = 'WRONG_MANAGER: %s, it should be %s' % (
                    response['reviewee'], reviewer.employee.manager)

        elif response['kind'] == EvalKind.MANAGER_PEER.name:
            reporters = employees_by_manager.get(reviewer.uid, [])
            if response['reviewee'] not in reporters:
                reason = 'WRONG_REPORTER: %s is not one of expected reporters. Reporters: %s' % (
                    response['reviewee'], reporters)

        return reason

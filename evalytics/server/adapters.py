from .models import EvalKind, Eval, Employee
from .models import EvalNode, EvalNodeSuite, OrgChart


class OrgChartAdapter:

    def create_initial_eval_suite(
            self, org_chart: OrgChart, consider_peers=None) -> EvalNodeSuite:
        """OrgChart => EvalNodeSuite

        by default it will only consider a '180' eval
        """
        eval_suite = EvalNodeSuite()

        for employee_node in org_chart:
            eval_suite.add_eval(EvalNode.new_self_eval(employee_node))

            supervisor = employee_node.parent
            if supervisor:
                eval_suite.add_eval(
                    EvalNode.new_supervisor_eval(employee_node, supervisor))
                if consider_peers:
                    for peer in supervisor.minions:
                        if peer is not employee_node:
                            eval_suite.add_eval(
                                EvalNode.new_peer_eval(employee_node, peer))

            for minion in employee_node.minions:
                eval_suite.add_eval(
                    EvalNode.new_minion_eval(employee_node, minion))

        return eval_suite


class EmployeeAdapter:

    def get_employees_by_manager(self, employees):
        managers = {
            employees[e.manager].uid:[]
            for uid, e in employees.items() if e.has_manager}

        for _, e in employees.items():
            if e.manager:
                managers[e.manager].append(e.uid)

        return managers

    def add_evals(self, employees, forms):
        employees_by_manager = self.get_employees_by_manager(employees)

        for uid, employee in employees.items():
            evals = []
            employee_forms = forms[employee.area]

            if employee.has_manager:
                evals.append(Eval(
                    reviewee=employee.manager,
                    kind=EvalKind.PEER_MANAGER,
                    form=employee_forms[EvalKind.PEER_MANAGER]))

            evals.append(Eval(
                reviewee=uid,
                kind=EvalKind.SELF,
                form=employee_forms[EvalKind.SELF]))

            if uid in employees_by_manager:
                for employee_uid in employees_by_manager[uid]:
                    evals.append(Eval(
                        reviewee=employee_uid,
                        kind=EvalKind.MANAGER_PEER,
                        form=employee_forms[EvalKind.MANAGER_PEER]))

            employee.evals = evals

        return employees

    def build_eval_message(self, employee: Employee):
        list_of_evals = ''
        for e_eval in employee.evals:
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
            </td></tr></tbody></tr></table></div>'''.format(employee.uid, list_of_evals)

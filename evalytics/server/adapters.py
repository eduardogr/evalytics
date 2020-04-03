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
        return """
You have new assignments:

    - eval self: %s
    - eval_manager: %s""" % (
        employee.eval_180.self_eval, 
        employee.eval_180.eval_manager)

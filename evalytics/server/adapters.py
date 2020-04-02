from .models import Eval, EvalSuite, OrgChart


class OrgChartAdapter:

    def create_initial_eval_suite(
            self, org_chart: OrgChart, consider_peers=None) -> EvalSuite:
        """OrgChart => EvalSuite

        by default it will only consider a '180' eval
        """
        eval_suite = EvalSuite()

        for employee_node in org_chart:
            eval_suite.add_eval(Eval.new_self_eval(employee_node))

            supervisor = employee_node.parent
            if supervisor:
                eval_suite.add_eval(
                    Eval.new_supervisor_eval(employee_node, supervisor))
                if consider_peers:
                    for peer in supervisor.minions:
                        if peer is not employee_node:
                            eval_suite.add_eval(
                                Eval.new_peer_eval(employee_node, peer))

            for minion in employee_node.minions:
                eval_suite.add_eval(
                    Eval.new_minion_eval(employee_node, minion))

        return eval_suite


class EmployeeAdapter:

    @classmethod
    def build_org_chart(cls, employees):
        # TODO: build OrgChart from list of employees
        pass

    @classmethod
    def build_eval_message(cls, employee):
        return """
You have new assignments:

    - eval self: %s
    - eval_manager: %s""" % (
        employee.eval_180.self_eval, 
        employee.eval_180.self_eval)

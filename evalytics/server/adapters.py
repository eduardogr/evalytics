from .models import Eval, EvalSuite, OrgChart


class OrgChartAdapter:

    def create_initial_eval_suite(
            self, org_chart: OrgChart, consider_peers=None) -> EvalSuite:
        """OrgChart => EvalSuite

        by default it will only consider a '180' eval
        """
        eval_suite = EvalSuite()

        for employee in org_chart:
            eval_suite.add_eval(Eval.new_self_eval(employee))

            supervisor = employee.parent
            if supervisor:
                eval_suite.add_eval(
                    Eval.new_supervisor_eval(employee, supervisor))
                if consider_peers:
                    for peer in supervisor.minions:
                        if peer is not employee:
                            eval_suite.add_eval(
                                Eval.new_peer_eval(employee, peer))

            for minion in employee.minions:
                eval_suite.add_eval(Eval.new_minion_eval(employee, minion))

        return eval_suite

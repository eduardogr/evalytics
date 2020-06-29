from evalytics.models import EvalKind, Eval, Reviewer, Employee
from evalytics.models import ReviewerResponse
from evalytics.config import Config
from evalytics.exceptions import MissingDataException

class EmployeeAdapter(Config):

    def get_employee_managers(self, employees, employee_uid):
        managers = []
        employee = employees.get(employee_uid, None)

        if employee is None:
            return managers

        employee_pointer = employee
        while employee_pointer is not None and employee_pointer.has_manager:
            managers.append(employee_pointer.manager)
            employee_pointer = employees.get(employee_pointer.manager, None)

        return managers

    def get_employees_by_manager(self, employees):
        managers = {
            employees[e.manager].uid:[]
            for uid, e in employees.items() if e.has_manager and e.manager in employees}

        for _, e in employees.items():
            if e.manager and e.manager in employees:
                managers[e.manager].append(e.uid)

        return managers

    def build_reviewers(self, employees, peers_assignment, forms):
        employees_by_manager = self.get_employees_by_manager(employees)

        reviewers = {}
        for uid, employee in employees.items():
            evals = []

            self.__check_area_exists_in_forms(forms, employee.area)

            employee_forms = forms[employee.area]

            evals.append(Eval(
                reviewee=uid,
                kind=EvalKind.SELF,
                form=employee_forms[EvalKind.SELF]))

            for peer in peers_assignment.get(uid, []):
                if peer not in employees:
                    raise MissingDataException("{} peer is not an employee".format(peer))

                if peer == uid:
                    continue

                if peer == employee.manager:
                    continue

                if peer in employees_by_manager.get(uid, []):
                    continue

                peer_employee = employees.get(peer)

                self.__check_area_exists_in_forms(forms, peer_employee.area)
                peer_forms = forms[peer_employee.area]

                evals.append(Eval(
                    reviewee=peer,
                    kind=EvalKind.PEER_TO_PEER,
                    form=peer_forms[EvalKind.PEER_TO_PEER]))

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

    def __check_area_exists_in_forms(self, forms, area):
        if area not in forms:
                raise MissingDataException("Missing area '{}' in forms".format(area))

class ReviewerAdapter(EmployeeAdapter):

    def get_status_from_responses(self, reviewers, responses):
        '''
        args:
            reviewers: {
                reviewer.uid: reviewer1,
                ...
                reviewerN.uid: reviewerN
            }

            responses: [
                ReviewerResponse(),
                ReviewerResponse(),
                ReviewerResponse()
            ]
        '''
        completed = {}
        pending = {}
        inconsistent = {}

        employees = {r.uid:r.employee for uid, r in reviewers.items()}
        employees_by_manager = super().get_employees_by_manager(employees)

        # Completed/Inconsistent reviews
        for uid, responses in responses.items():
            completed_responses = {}
            inconsistent_responses = {}
            for response in responses:
                if uid not in reviewers:
                    continue

                reviewer = reviewers[uid]
                inconsistent_reason = self.__get_reason_of_inconsistent_response(
                    reviewer,
                    response,
                    employees_by_manager
                )

                if inconsistent_reason is None:
                    completed_responses.update({
                        response.reviewee: {
                            'kind': response.eval_kind.name,
                        }
                    })
                else:
                    inconsistent_responses.update({
                        response.reviewee: {
                            'kind': response.eval_kind.name,
                            'reason': inconsistent_reason,
                            'filename': response.filename,
                            'line_number': response.line_number,
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

        # Pending reviews
        for uid, reviewer in reviewers.items():
            evals = reviewer.evals
            pending_evals = []
            for e in evals:
                if e.reviewee not in completed.get(uid, {}):
                    pending_evals.append(e)

            if len(pending_evals) > 0:
                pending.update({
                    reviewer.uid: Reviewer(
                        employee=reviewer.employee,
                        evals=pending_evals
                    )
                })

        return completed, pending, inconsistent

    def __get_reason_of_inconsistent_response(self,
                                              reviewer: Reviewer,
                                              response: ReviewerResponse,
                                              employees_by_manager):
        reason = None
        if response.eval_kind == EvalKind.PEER_MANAGER:
            if reviewer.employee.manager != response.reviewee:
                reason = "WRONG_MANAGER: '%s', it should be '%s'." % (
                    response.reviewee, reviewer.employee.manager)

        elif response.eval_kind == EvalKind.MANAGER_PEER:
            reporters = employees_by_manager.get(reviewer.uid, [])
            if response.reviewee not in reporters:
                reason = "WRONG_REPORTER: '%s' is not one of expected reporters. Reporters: %s." % (
                    response.reviewee, reporters)

        return reason

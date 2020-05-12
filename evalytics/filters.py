
from .exceptions import NotExistentEmployeeException

class ReviewerResponseFilter:

    def filter_reviewees(self,
                         reviewee_evaluations,
                         employees,
                         area,
                         managers,
                         allowed_uids):
        if area is not None:
            reviewee_evaluations = self.__filter_reviewees_by_area(
                reviewee_evaluations,
                employees,
                area)
        elif managers is not None:
            reviewee_evaluations = self.__filter_reviewees_by_allowed_managers(
                reviewee_evaluations,
                employees,
                managers)
        elif allowed_uids is not None:
            reviewee_evaluations = self.__filter_reviewees_by_allowed_uids(
                reviewee_evaluations,
                allowed_uids)

        return reviewee_evaluations

    def __filter_reviewees_by_area(self, reviewee_evaluations, employees, area):
        allowed_evaluations = {}
        for uid, evals in reviewee_evaluations.items():
            self.__check_employee(uid, employees)
            employee = employees[uid]
            if employee.area == area:
                allowed_evaluations.update({
                    uid: evals
                })

        return allowed_evaluations

    def __filter_reviewees_by_allowed_managers(self, reviewee_evaluations, employees, managers):
        allowed_evaluations = {}
        for uid, evals in reviewee_evaluations.items():
            self.__check_employee(uid, employees)
            employee = employees[uid]
            if employee.has_manager and employee.manager in managers:
                allowed_evaluations.update({
                    uid: evals
                })

        return allowed_evaluations

    def __filter_reviewees_by_allowed_uids(self, reviewee_evaluations, allowed_uids):
        allowed_evaluations = {}
        for uid, evals in reviewee_evaluations.items():
            if uid in allowed_uids:
                allowed_evaluations.update({
                    uid: evals
                })

        return allowed_evaluations

    def __check_employee(self, uid, employees):
        if uid not in employees:
            raise NotExistentEmployeeException("{} does not exist".format(uid))

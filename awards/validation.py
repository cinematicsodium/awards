from utils import get_max_limits, is_compensation_within_limits
from alerts import gen_ind_limit_alert, gen_grp_limit_alert
from modules import EmpInfo, IndAwd


def validate_ind_compensation(ind_details: IndAwd) -> None:
    employee = ind_details.employee
    value = ind_details.value
    extent = ind_details.extent
    max_monetary, max_hours = get_max_limits(value, extent)
    if is_compensation_within_limits(employee.monetary, employee.hours, max_monetary, max_hours):
        return

    invalid_ind_msg = gen_ind_limit_alert(employee, value, extent)
    raise ValueError(invalid_ind_msg)


def validate_grp_compensation(employees: list[EmpInfo], value: str, extent: str) -> None:
    max_monetary, max_hours = get_max_limits(value, extent)
    monetary_sum = sum(emp.monetary for emp in employees)
    hours_sum = sum(emp.hours for emp in employees)
    
    if is_compensation_within_limits(monetary_sum, hours_sum, max_monetary, max_hours):
        return
    
    invalid_grp_msg = gen_grp_limit_alert(employees, value, extent)
    raise ValueError(invalid_grp_msg)
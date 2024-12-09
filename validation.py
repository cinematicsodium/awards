from alerts import gen_ind_limit_alert,gen_grp_limit_alert
from utils import get_max_limits,is_compensation_valid
from constants import VALUE_IDX_MAP, EXTENT_IDX_MAP
from modules import EmpInfo, IndAwd, GrpAwd


def validate_value_and_extent(value: str, extent: str) -> bool:
    return all([
        value in VALUE_IDX_MAP.keys(),
        extent in EXTENT_IDX_MAP.keys()
    ])

def validate_ind_compensation(ind_details: IndAwd) -> None:
    employee = ind_details.employee
    value = ind_details.value
    extent = ind_details.extent

    is_valid_val_ext: bool = validate_value_and_extent(value, extent)
    if not is_valid_val_ext:
        return

    max_monetary, max_hours = get_max_limits(value, extent)
    if is_compensation_valid(employee.monetary, employee.hours, max_monetary, max_hours):
        return

    invalid_ind_msg = gen_ind_limit_alert(employee, value, extent)
    raise ValueError(invalid_ind_msg)


def validate_ind_fields(ind_details: IndAwd) -> None:
    required_fields: dict = {
        'log ID': ind_details.id,
        'nominator name': ind_details.nominator,
        'funding org': ind_details.funding_org,
        'justification': ind_details.justification,
        'nominee name': ind_details.employee.name,
    }

    missing_fields = [field for field,value in required_fields.items() if not value]

    if missing_fields:
        linebreak = '\n- '
        raise ValueError(
            f'Missing required fields:\n'
            f'{linebreak.join(missing_fields)}'
        )

def validate_grp_compensation(employees: list[EmpInfo], value: str, extent: str) -> None:
    is_valid_val_ext: bool = validate_value_and_extent(value, extent)
    if not is_valid_val_ext:
        return

    max_monetary, max_hours = get_max_limits(value, extent)
    monetary_sum = sum(emp.monetary for emp in employees)
    hours_sum = sum(emp.hours for emp in employees)

    if is_compensation_valid(monetary_sum, hours_sum, max_monetary, max_hours):
        return

    invalid_grp_msg = gen_grp_limit_alert(employees, value, extent)
    raise ValueError(invalid_grp_msg)

def validate_grp_fields(ind_details: GrpAwd) -> None:
    required_fields: dict = {
        'log ID': ind_details.id,
        'nominator name': ind_details.nominator,
        'funding org': ind_details.funding_org,
        'justification': ind_details.justification,
        'nominees': ind_details.employees,
    }

    missing_fields = [field for field,value in required_fields.items() if not value]

    if missing_fields:
        linebreak = '\n- '
        raise ValueError(
            f'Missing required fields:\n'
            f'{linebreak.join(missing_fields)}'
        )
from validation import validate_grp_compensation, validate_grp_fields
from modules import EmpInfo, GrpAwd, PDFInfo
from formatting import Formatting
from grpConfig import GrpConfig
from constants import PAY_PLANS
from logger import SimpleLogger
from utils import generate_id
from fieldFuncs import *

def get_team_name(first_page_fields: dict) -> str:
    group_name_key: str = 'employee name'
    return first_page_fields.get(group_name_key, '')

def get_grp_emp_name(mid_section: dict[str,str], name_key: str) -> str:
    name_val: str = mid_section.get(name_key, '')
    return Formatting.name(name_val)

def get_grp_emp_supervisor(mid_section: dict[str,str], supervisor_key: str) -> str:
    supervisor_val: str = mid_section.get(supervisor_key, '')
    return Formatting.name(supervisor_val)

def get_grp_emp_org(mid_section: dict[str,str], org_key: str) -> str:
    return mid_section.get(org_key, '')

def get_grp_emp_pay_plan(mid_section: dict[str,str], pay_plan_key: str) -> str:
    pay_plan_val: str = mid_section.get(pay_plan_key, '-')
    for pay_plan in PAY_PLANS:
        if pay_plan_val.upper().startswith(pay_plan):
            return pay_plan
    return pay_plan_val

def get_grp_emp_monetary(mid_section: dict[str,str], monetary: str) -> float:
    monetary_val: str = mid_section.get(monetary, '')
    return Formatting.numerical(monetary_val)

def get_grp_emp_hours(mid_section: dict[str,str], hours: str) -> float:
    hours_val: str = mid_section.get(hours, '')
    return Formatting.numerical(hours_val)

def is_valid_employee(employee: EmpInfo) -> bool:
    award_values: bool = any([employee.monetary, employee.hours])
    return all([
        employee.name,
        award_values
    ])

def get_grp_employees(grp_config: list[EmpInfo], mid_section: dict[str,str]) -> list[EmpInfo]:
    employees_list: list[EmpInfo] = []
    detected_employee_set: set = set()
    valid_employee_set: set = set()

    for employee_config in grp_config:
        name_key: str = employee_config.name
        raw_name: str = mid_section.get(name_key, '')
        formatted_name: str = Formatting.name(raw_name)
        if formatted_name:
            detected_employee_set.add(formatted_name)
            employee: EmpInfo = EmpInfo(
                name=formatted_name,
                supervisor=get_grp_emp_supervisor(mid_section, employee_config.supervisor),
                org=get_grp_emp_org(mid_section, employee_config.org),
                pay_plan=get_grp_emp_pay_plan(mid_section, employee_config.pay_plan),
                monetary=get_grp_emp_monetary(mid_section, employee_config.monetary),
                hours=get_grp_emp_hours(mid_section, employee_config.hours),
            )
            if is_valid_employee(employee):
                employees_list.append(employee)
                valid_employee_set.add(formatted_name)

    missing_employees: set = detected_employee_set - valid_employee_set
    if missing_employees:
        formatted_employee_list = '\n- '.join(list(missing_employees))
        raise ValueError(
            'Unable to process the following employees:\n'
            f'{formatted_employee_list}'
            )

    return employees_list


def get_grp_award_details(pdf_info: PDFInfo) -> GrpAwd:
    grp_config: list[EmpInfo] = GrpConfig.get(pdf_info.page_count)
    if not grp_config:
        raise ValueError(f'No group configuration found for {pdf_info.page_count} pages')

    grp_award_details: GrpAwd = GrpAwd(
        id = generate_id(pdf_info.file_name, pdf_info.fiscal_year, pdf_info.serial_number, grp=True),
        type = determine_award_type(pdf_info.first_page),
        nominator = get_nominator_name(pdf_info.first_page),
        funding_org = determine_main_funding_org(pdf_info.first_page),
        justification = get_justification(pdf_info.last_page),
        value = get_value(pdf_info.last_page),
        extent = get_extent(pdf_info.last_page),
        date_received = determine_date_received(pdf_info.first_page),
        team_name = get_team_name(pdf_info.first_page),
        employees = get_grp_employees(grp_config, pdf_info.mid_section),
    )
    validate_grp_compensation(grp_award_details.employees, grp_award_details.value, grp_award_details.extent)
    validate_grp_fields(grp_award_details)

    return grp_award_details

if __name__ == '__main__':
    pass

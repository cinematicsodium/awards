from dataclasses import dataclass
from typing import NamedTuple

# Define structure for each employee award entry
class EmployeeDetails(NamedTuple):
    name: str
    pay_plan: str
    org: str
    monetary_award: str
    time_off_hours: str
    supervisor_name: str

employee_details_max_7 = (
    EmployeeDetails('employee name_1', 'pay plan  gradestep_1', 'organization_7', 'award amount', 'time off hours', 'immediate supervisor'),
    EmployeeDetails('employee name_3', 'pay plan  gradestep_3', 'organization_8', 'award amount_2', 'time off hours_2', 'immediate supervisor_2'),
    EmployeeDetails('employee name_4', 'pay plan  gradestep_4', 'organization_9', 'award amount_3', 'time off hours_3', 'immediate supervisor_3'),
    EmployeeDetails('employee name_5', 'pay plan  gradestep_5', 'organization_10', 'award amount_4', 'time off hours_4', 'immediate supervisor_4'),
    EmployeeDetails('employee name_6', 'pay plan  gradestep_6', 'organization_11', 'award amount_5', 'time off hours_5', 'immediate supervisor_5'),
    EmployeeDetails('employee name_7', 'pay plan  gradestep_7', 'organization_12', 'award amount_6', 'time off hours_6', 'immediate supervisor_6'),
    EmployeeDetails('employee name_8', 'pay plan  gradestep_8', 'organization_13', 'award amount_7', 'time off hours_7', 'immediate supervisor_7'),
)

@dataclass
class IndConfig:
    group_name: str = "group name"
    funding_org: str = "organization"
    sasMonetary: str = "undefined"
    sasTimeOff: str = "hours_2"
    nominator: str = "please print"
    nominator_org: str = "org"
    date_received: str = "date received"
    employees: tuple = employee_details_max_7
    extent: str = ""
    justification: str = "extent of application"
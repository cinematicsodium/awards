from dataclasses import dataclass

from configs.employees import (
    max7_employees,
    max14_employees_var1,
    max14_employees_var2,
    max21_employees_var1,
    max21_employees_var2,
)


@dataclass
class AwardDetails:
    sasMonetary: str = "undefined"
    sasTimeOff: str = "hours_2"
    otsMonetary: str = "on the spot award"
    otsTimeOff: str = "hours"
    nominator_name: str = "please print"
    nominator_org: str = "org"
    approving_org: str = "org_4"


@dataclass
class GroupAwardDetails(AwardDetails):
    group_name: str = "group name"
    funding_org: str = "organization"
    date_received: str = "date received"
    employees: tuple
    value: str = ""
    extent: str = ""
    justification: str = "extent of application"


@dataclass
class GroupMax7(GroupAwardDetails):
    employees = max7_employees
GROUP_MAX_7 = GroupMax7()

@dataclass
class GroupMax14Var1(GroupAwardDetails):
    employees = max14_employees_var1
GROUP_MAX_14_VAR1 = GroupMax14Var1()

@dataclass
class GroupMax14Var2(GroupAwardDetails):
    group_name = "employee name"
    nominator_name = "special act award funding string 2"
    nominator_org = "org_2"
    employees = max14_employees_var2
GROUP_MAX_14_VAR2 = GroupMax14Var2()

@dataclass
class GroupMax21Var1(GroupAwardDetails):
    employees = max21_employees_var1
GROUP_MAX_21_VAR1 = GroupMax21Var1()

@dataclass
class GroupMax21Var2(GroupAwardDetails):
    employees = max21_employees_var2
GROUP_MAX_21_VAR2 = GroupMax21Var2()
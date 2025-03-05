from dataclasses import dataclass
from typing import NamedTuple


@dataclass
class GroupAwardDetails:
    group_name: str
    funding_org: str
    sasMonetary: str
    sasTimeOff: str
    nominator: str
    nominator_org: str
    date_received: str
    employees: tuple
    value: str
    extent: str
    justification: str


@dataclass
class GroupAwardDetailsMax7:
    group_name: str = "group name"
    funding_org: str = "organization"
    sasMonetary: str = "undefined"
    sasTimeOff: str = "hours_2"
    nominator: str = "please print"
    nominator_org: str = "org"
    date_received: str = "date received"
    employees: tuple = ()
    value: str = ""
    extent: str = ""
    justification: str = "extent of application"


# Max7

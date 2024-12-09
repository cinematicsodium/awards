from dataclasses import dataclass, field
from typing import NamedTuple


class FiscalYear(NamedTuple):
    year: str
    submissions_inbox: str
    serial_numbers_json: str
    award_details_TSV: str
    award_details_txt: str
    archived_items_folder: str
    rejected_items_folder: str
    def __str__(self):
        return (f'year: {self.year}\n'
                f'newly_received_folder:  {self.submissions_inbox}\n'
                f'serial_numbers_json:    {self.serial_numbers_json}\n'
                f'award_details_TSV:      {self.award_details_TSV}\n'
                f'award_details_txt:      {self.award_details_txt}\n'
                f'archived_items_folder:  {self.archived_items_folder}\n'
                f'rejected_items_folder:  {self.rejected_items_folder}'
        )


@dataclass
class PDFInfo:
    first_page: dict = field(default_factory=dict)
    mid_section: dict = field(default_factory=dict)
    last_page: dict = field(default_factory=dict)
    file_name: str = ''
    category: str = ''
    fiscal_year: str = ''
    serial_number: int = 0
    page_count: int = 0


@dataclass
class SerialNumbers:
    IND: int
    GRP: int


@dataclass
class JustifInfo:
    text: str = ''
    length: int = 0


@dataclass
class EmpInfo:
    name: str = ''
    monetary: float = 0.0
    hours: float = 0.0
    org: str = ''
    pay_plan: str = ''
    supervisor: str = ''


@dataclass
class AwardDetails:
    id: str = ''
    category: str = ''
    type: str = ''
    nominator: str = ''
    funding_org: str = ''
    justification: JustifInfo = field(default_factory=JustifInfo)
    value: str = ''
    extent: str = ''
    date_received: str = ''


@dataclass
class IndAwd(AwardDetails):
    employee: EmpInfo = field(default_factory=EmpInfo)
    category: str = 'IND'
    def __str__(self):
        return (f'id:             {self.id}\n'
                f'date_received:  {self.date_received}\n'
                f'funding_org:    {self.funding_org}\n'
                f'category:       {self.category}\n'
                f'type:           {self.type}\n'
                f'nominator:      {self.nominator}\n'
                f'justification:  {self.justification.length} words\n'
                f'value:          {self.value}\n'
                f'extent:         {self.extent}\n'
                f'employee:       {self.employee.name}\n'
                f'monetary:       ${self.employee.monetary:0,.2f}\n'
                f'time-off:       {self.employee.hours} hours'
        )


@dataclass
class GrpAwd(AwardDetails):
    employees: list[EmpInfo] = field(default_factory=list)
    category: str = 'GRP'
    team_name: str = ''
    def __str__(self):

        max_name_len = max([len(employee.name) for employee in self.employees]) + 4
        max_monetary_len = max([len(str(employee.monetary)) for employee in self.employees]) + 4

        formatted_employee_list = '\n'.join([
            f'  - {employee.name.ljust(max_name_len)}'
            f'Monetary: ${str(employee.monetary).ljust(max_monetary_len)}'
            f'{int(employee.hours)} hours'
            for employee in self.employees
        ])

        return (f'id:             {self.id}\n'
                f'date_received:  {self.date_received}\n'
                f'category:       {self.category}\n'
                f'funding_org:    {self.funding_org}\n'
                f'type:           {self.type}\n'
                f'nominator:      {self.nominator}\n'
                f'justification:  {self.justification.length} words\n'
                f'value:          {self.value}\n'
                f'extent:         {self.extent}\n'
                f'group name:     {self.team_name}\n'
                f'employees:\n'
                f'{formatted_employee_list}'
        )




from dataclasses import dataclass, field


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
    supervisor: str = ''
    org: str = ''
    pay_plan: str = ''
    monetary: float = 0.0
    hours: float = 0.0
    valid: bool = True
    def __str__(self):
        return (f'\n\tname: {self.name}\n'
                f'\tsupervisor: {self.supervisor}\n'
                f'\torg: {self.org}\n'
                f'\tpay_plan: {self.pay_plan}\n'
                f'\tmonetary: {self.monetary}\n'
                f'\thours: {self.hours}'
        )


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
                f'funding_org:    {self.funding_org}\n'
                f'category:       {self.category}\n'
                f'type:           {self.type}\n'
                f'nominator:      {self.nominator}\n'
                f'justification:  {self.justification.length} words\n'
                f'value:          {self.value}\n'
                f'extent:         {self.extent}\n'
                f'date_received:  {self.date_received}\n'
                f'employee:       {self.employee}'
        )


@dataclass
class GrpAwd(AwardDetails):
    employees: list[EmpInfo] = field(default_factory=list)
    category: str = 'GRP'
    def __str__(self):
        max_name_len = max([len(employee.name) for employee in self.employees]) + 4
        max_monetary_len = max([len(str(employee.monetary)) for employee in self.employees]) + 4
        
        formatted_employee_list = '\n'.join([
            f'{employee.name.ljust(max_name_len)}'
            f'${str(employee.monetary).ljust(max_monetary_len)}'
            f'{employee.hours} hours'
            for employee in self.employees
        ])
        
        return (f'id: {self.id}\n'
                f'category: {self.category}\n'
                f'type: {self.type}\n'
                f'nominator: {self.nominator}\n'
                f'funding_org: {self.funding_org}\n'
                f'justification: {self.justification.length} words\n'
                f'value: {self.value}\n'
                f'extent: {self.extent}\n'
                f'date_received: {self.date_received}\n'
                f'employees: \n{formatted_employee_list}\n'
        )




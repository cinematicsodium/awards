from utils import get_max_limits
from modules import EmpInfo


HEADER = 'Award amounts exceed the maximum allowed based on the selected award value and extent.'
POLICY = '# Insert_NAP_Policy'
FOOTER = '\n\n'.join([
    'Please make the appropriate corrections and resubmit for processing.',
    'Thank you.'
])


def gen_ind_limit_alert(employee: EmpInfo, value: str, extent: str):
    max_monetary, max_hours = get_max_limits(value, extent)

    value, extent = value.title(), extent.title()

    monetary_ratio = employee.monetary / max_monetary
    hours_ratio = employee.hours / max_hours

    monetary_str = f'{employee.monetary:0,.2f}'.ljust(11)
    hours_str = f'{employee.hours} hours'.ljust(12)
    ratio_str = f'{monetary_ratio + hours_ratio:.2%}'.ljust(12)

    return (
f"""{HEADER}

Award Details:
- Value:       {value}
- Extent:      {extent}

({value} x {extent}) Limits:
- Monetary:    ${max_monetary}
- Time-Off:    {max_hours} hours

Nominee Details:
- Name:        {employee.name}
- Monetary:    ${monetary_str}< {monetary_ratio:.2%} of ${max_monetary:.2f} limit
- Time-Off:    {hours_str}< {hours_ratio:.2%} of {max_hours}-hour limit
- Total:       {ratio_str}< Max Allowed: 100%

{POLICY}

{FOOTER}"""
    )


def gen_grp_limit_alert(employees: list[EmpInfo], value: str, extent: str):
    max_monetary, max_hours = get_max_limits(value, extent)

    monetary_sum = sum(emp.monetary for emp in employees)
    hours_sum = sum(emp.hours for emp in employees)

    monetary_ratio = monetary_sum / max_monetary
    hours_ratio = hours_sum / max_hours
    sum_ratio = monetary_ratio + hours_ratio

    monetary_sum = f'{monetary_sum:,.2f}'.ljust(11)
    hours_sum = f'{hours_sum} hours'.ljust(12)
    sum_ratio = f'{sum_ratio:.2%}'.ljust(12)

    max_name_len = max(len(emp.name) for emp in employees) + 4
    max_monetary_len = max(len(str(emp.monetary)) for emp in employees) + 4

    value, extent = value.title(), extent.title()

    employee_details = '\n'.join(
        f'- Name: {emp.name.ljust(max_name_len)}'
        f'Monetary: ${str(emp.monetary).ljust(max_monetary_len)}'
        f'Time-Off: {emp.hours}' for emp in employees)
    return (
f"""{HEADER}

Award Details:
- Value:       {value}
- Extent:      {extent}

({value} x {extent}) Limits:
- Monetary:    ${max_monetary:,.2f}
- Time-Off:    {max_hours:,} hours

Nominee Details:
{employee_details}

Totals:
- Monetary:    ${monetary_sum}< {monetary_ratio:.2%} of ${max_monetary:,.2f} limit
- Time-Off:    {hours_sum}< {hours_ratio:.2%} of {max_hours:,}-hour limit
- Sum:         {sum_ratio}< Max Allowed: 100%

{POLICY}

{FOOTER}"""
    )

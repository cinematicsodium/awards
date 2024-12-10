from validation import *
from modules import EmpInfo, PDFInfo, SerialNumbers
from constants import IND_FIELDS, PAY_PLANS
from formatting import Formatting
from utils import generate_id
from fieldFuncs import *


def get_ind_name(first_page_fields: dict) -> str:
    return Formatting.name(first_page_fields.get(IND_FIELDS.employee_name, ''))


def get_ind_supervisor(first_page_fields: dict) -> str:
    return Formatting.name(first_page_fields.get(IND_FIELDS.supervisor, ''))


def get_ind_org(first_page_fields: dict) -> str:
    return first_page_fields.get(IND_FIELDS.employee_org, '')


def get_ind_money(first_page_fields: dict) -> float:
    sas_money = Formatting.numerical(first_page_fields.get(IND_FIELDS.sas_fields.monetary, ''))
    ots_money = Formatting.numerical(first_page_fields.get(IND_FIELDS.ots_fields.monetary, ''))
    if sas_money and ots_money:
        raise ValueError(
            f'Multiple monetary values found.\n'
            f'SAS: ${sas_money:.2f}\n'
            f'OTS: ${ots_money:.2f}\n'
        )
    if not sas_money and not ots_money:
        return 0.0
    return max(sas_money, ots_money)


def get_ind_time(first_page_fields: dict) -> float:
    sas_time = Formatting.numerical(first_page_fields.get(IND_FIELDS.sas_fields.hours, ''))
    ots_time = Formatting.numerical(first_page_fields.get(IND_FIELDS.ots_fields.hours, ''))
    if sas_time and ots_time:
        raise ValueError(
            f'Multiple time-off values found.\n'
            f'SAS: {str(sas_time).zfill(2)} hour(s)\n'
            f'OTS: {str(ots_time).zfill(2)} hour(s)\n'
        )
    if not sas_time and not ots_time:
        return 0.0
    return max(sas_time, ots_time)


def get_ind_pay_plan(first_page_fields: dict) -> str:
    pay_plan_val: str = max(
        first_page_fields.get(IND_FIELDS.employee_pay_plan_1, ''),
        first_page_fields.get(IND_FIELDS.employee_pay_plan_2, ''),
        )
    pay_plan_val = [pay_plan for pay_plan in PAY_PLANS if pay_plan_val.upper().startswith(pay_plan)]
    if len(pay_plan_val) != 1:
        return '-'
    return pay_plan_val[0]


def get_ind_employee(first_page_fields: dict) -> EmpInfo:
    ind_employee = EmpInfo(
        name = get_ind_name(first_page_fields),
        supervisor = get_ind_supervisor(first_page_fields),
        org = get_ind_org(first_page_fields),
        pay_plan = get_ind_pay_plan(first_page_fields),
        monetary = get_ind_money(first_page_fields),
        hours = get_ind_time(first_page_fields),
    )
    return ind_employee


def get_ind_award_details(pdf_info: PDFInfo) -> IndAwd:
    ind_award_details = IndAwd(
        id = generate_id(pdf_info.file_name, pdf_info.fiscal_year, pdf_info.serial_number),
        type = determine_award_type(pdf_info.first_page),
        nominator = get_nominator_name(pdf_info.first_page),
        funding_org = determine_main_funding_org(pdf_info.first_page),
        justification = get_justification(pdf_info.last_page),
        value = get_value(pdf_info.last_page),
        extent = get_extent(pdf_info.last_page),
        date_received =determine_date_received(pdf_info.first_page),
        employee = get_ind_employee(pdf_info.first_page),
    )

    validate_ind_fields(ind_award_details)
    validate_ind_compensation(ind_award_details)

    return ind_award_details

if __name__ == '__main__':
    pass

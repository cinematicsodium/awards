from constants import COMMON_FIELDS
from formatting import Formatting
from collections import Counter
from modules import JustifInfo
from datetime import datetime
from orgConfig import ORGS


def get_nominator_name(first_page_fields: dict) -> str:
    nominator = Formatting.name(first_page_fields.get(COMMON_FIELDS.nominator_name, ''))
    return nominator if nominator else ''


def find_main_org(org_fields_list: list[str]) -> str:
    org_list = []
    divs = [div for org in ORGS for div in org]
    for org_field in org_fields_list:
        for div in divs:
            if div in org_field:
                div = [org[0] for org in ORGS if org[0] in div]
                org_list.extend(div)

    return org_list

def determine_main_funding_org(first_page_fields: dict) -> str:
    org_fields_list: list[str] = [
        first_page_fields.get(funding_org_field)
        for funding_org_field in COMMON_FIELDS.funding_orgs
        if first_page_fields.get(funding_org_field)
    ]
    if not org_fields_list:
        return ''

    main_orgs = find_main_org(org_fields_list)
    if not main_orgs:
        return ''

    org_counter = Counter(main_orgs)
    most_common_org, _ = org_counter.most_common(1)[0]
    return most_common_org


def determine_award_type(first_page_fields: dict) -> str:
    sas_fields = (COMMON_FIELDS.sas_fields.combined())
    ots_fields = (COMMON_FIELDS.ots_fields.combined())

    sas_count = sum(1 for k in first_page_fields.keys() if k in sas_fields)
    ots_count = sum(1 for k in first_page_fields.keys() if k in ots_fields)

    if sas_count > ots_count:
        return 'SAS'
    elif ots_count > sas_count:
        return 'OTS'
    return ''


def get_justification(last_page_fields: dict) -> JustifInfo:
    justification = JustifInfo()
    justification_text = last_page_fields.get(COMMON_FIELDS.justification, '')
    if justification_text:
        justification.text = Formatting.justification(field_text=justification_text)
        justification.length = len(justification.text.split())
    return justification


def get_value(last_page_fields: dict[str,str]) -> str:
    value_fields = [
        k for k, v in last_page_fields.items()
        if k.lower() in COMMON_FIELDS.values
        and str(v).lower() == 'on'
    ]

    if len(value_fields) != 1:
        return ''

    return value_fields[0]


def get_extent(last_page_fields: dict[str,str]) -> str:
    extent_fields = [
        k.lower() for k, v in last_page_fields.items()
        if k.lower() in COMMON_FIELDS.extents
        and str(v).lower() == 'on'
    ]

    if len(extent_fields) != 1:
        return ''

    return extent_fields[0]


def get_date_received(first_page_fields: dict) -> str:
    return first_page_fields.get(COMMON_FIELDS.date_received, '')


def determine_date_received(first_page_fields: dict) -> str:
    current_date = datetime.now().strftime('%Y-%m-%d')

    date_received: str = get_date_received(first_page_fields)

    if date_received:
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d', '%Y-%m-%d',
            '%d %b %Y', '%d %B %Y', '%b %d, %Y', '%B %d, %Y'
        ]
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(date_received, date_format)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
    return current_date


if __name__ == '__main__':
    pass
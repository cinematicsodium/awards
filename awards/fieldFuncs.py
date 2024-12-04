from constants import COMMON_FIELDS
from formatting import Formatting
from modules import JustifInfo
from datetime import datetime

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SHARED FUNCTIONS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_nominator_name(first_page_fields: dict) -> str:
    nominator = Formatting.name(first_page_fields.get(COMMON_FIELDS.nominator_name, ''))
    return nominator if nominator else ''


def get_funding_org(first_page_fields: dict) -> list[str]:
    return [
        first_page_fields.get(funding_org)
        for funding_org in COMMON_FIELDS.funding_orgs
        if first_page_fields.get(funding_org)
    ]


def get_type(first_page_fields: dict) -> str:
    sas_fields = (COMMON_FIELDS.sas_fields.monetary, COMMON_FIELDS.sas_fields.hours)
    ots_fields = (COMMON_FIELDS.ots_fields.monetary, COMMON_FIELDS.ots_fields.hours)

    sas_count = sum(1 for k in first_page_fields if k in sas_fields)
    ots_count = sum(1 for k in first_page_fields if k in ots_fields)
    type = ''
    if sas_count > ots_count:
        type = 'SAS'
    elif ots_count > sas_count:
        type = 'OTS'
    return type


def get_justification(last_page_fields: dict) -> JustifInfo:
    justification = JustifInfo()
    justification_text = last_page_fields.get(COMMON_FIELDS.justification, '')
    if justification_text:
        justification.text = Formatting.justification(field_text=justification_text)
        justification.length = len(justification.text.split())
    return justification


def get_value(last_page_fields: dict) -> str:
    value_fields = [
        k for k, v in last_page_fields.items()
        if k in COMMON_FIELDS.values
        and str(v).lower() == 'on'
    ]

    if len(value_fields) != 1:
        return ''

    return value_fields[0]


def get_extent(last_page_fields: dict) -> str:
    extent_fields = [
        k for k, v in last_page_fields.items()
        if k in COMMON_FIELDS.extents
        and str(v).lower() == 'on'
    ]

    if len(extent_fields) != 1:
        return ''

    return extent_fields[0]


def determine_date_received(first_page_fields: dict) -> str:
    date_received: str = first_page_fields.get(COMMON_FIELDS.date_received, '')

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
    return datetime.now().strftime('%Y-%m-%d')



if __name__ == '__main__':
    pass
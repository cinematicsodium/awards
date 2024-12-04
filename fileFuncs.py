from constants import PAGE_COUNTS
from datetime import datetime
from modules import *
from typing import Any
import fitz
import json
import os


def get_serial_numbers(file_path: str) -> SerialNumbers:
    with open(file_path, 'r') as file:
        data = json.load(file)
    serial_numbers = SerialNumbers(
        IND = data.get('IND', []),
        GRP = data.get('GRP', []),
    )
    if not all([
        serial_numbers.IND,
        serial_numbers.GRP,
    ]):
        raise ValueError('Serial Numbers: (not valid)')

    return serial_numbers


def is_valid_field(val: Any) -> bool:
    return all([
        val,
        isinstance(val,str),
        str(val).lower() != 'off',
    ])


def determine_award_category(page_count: int) -> str:
    if page_count == PAGE_COUNTS.ind:
        return 'IND'
    elif page_count in [PAGE_COUNTS.grp_max_7, PAGE_COUNTS.grp_max_14, PAGE_COUNTS.grp_max_21]:
        return 'GRP'
    else:
        raise ValueError(f'Page Count: {page_count} (not valid)')


def get_pdf_info(file_path: str, fy: str, ser_num: int) -> PDFInfo:
    pdf_info = PDFInfo(
        file_name = os.path.basename(file_path),
        serial_number = ser_num,
        fiscal_year = fy,
    )
    with fitz.open(file_path) as doc:
        page_count: int = doc.page_count
        first_page: int = 0
        last_page: int = page_count - 1
        pdf_info.category = determine_award_category(page_count)
        pdf_info.page_count = page_count

        field_count: int = 0
        for page in doc:
            current_page: int = page.number
            fields: Any = [field for field in page.widgets() if is_valid_field(field.field_value.strip())]
            field_count += len(fields)
            for field in fields:
                key: str = field.field_name.strip().lower()
                val: str = field.field_value.strip()

                if current_page == first_page:
                    pdf_info.first_page[key] = val
                elif current_page == last_page:
                    pdf_info.last_page[key] = val
                else:
                    pdf_info.mid_section[key] = val

        if field_count <= 10:
            raise ValueError(f'Field Count: {field_count} (not enough fields found)')
    return pdf_info


def export_as_TSV(file_path: str, award_data: IndAwd | GrpAwd) -> None:
    fields = [
        award_data.id,
        award_data.date_received,
        "",  # date processed
        "",  # name
        award_data.category,
        award_data.type,
        "",  # monetary
        "",  # hours
        award_data.nominator,
        str(award_data.funding_org),
        "",  # MB div
        award_data.justification.text,
        award_data.value,
        award_data.extent
    ]

    with open(file_path, 'a') as f:
        if award_data.category == 'IND':
            fields[3] = award_data.employee.name
            fields[6] = str(award_data.employee.monetary)
            fields[7] = str(award_data.employee.hours)
            f.write("\t".join(fields) + '\n')
        elif award_data.category == 'GRP':
            for employee in award_data.employees:
                fields[3] = employee.name
                fields[6] = str(employee.monetary)
                fields[7] = str(employee.hours)
                f.write("\t".join(fields) + '\n')


def insert_date_received(filePath: str, date_received: str) -> None:
    with fitz.open(filePath) as doc:
        for page in doc:
            date_field = [field for field in page.widgets() if field.field_name.lower() == 'date received']
            if len(date_field) == 1:
                date_xref = date_field[0].xref
                date = page.load_widget(date_xref)
                date.field_value = date_received
                date.update()
                doc.saveIncr()
            # for field in page.widgets():
            #     fkey: str = field.field_name.lower()
            #     fxrf: int = field.xref
            #     if fkey == "date received":
            #         date = page.load_widget(fxrf)
            #         date.field_value = award_data["Date Received"]
            #         date.update()
            #         doc.saveIncr()


def save_serial_numbers(file_path: str, serial_numbers: SerialNumbers) -> None:
    with open(file_path, 'w') as file:
        json.dump(serial_numbers.__dict__, file, indent=4)


def generate_new_file_name(award_details: IndAwd | GrpAwd, grp: bool = False) -> str:
    if not grp:
        return ' _ '.join([
            award_details.id,
            award_details.funding_org,
            award_details.employee.name,
            award_details.date_received
        ]) + '.pdf'

    elif grp:
        return ' _ '.join([
            award_details.id,
            award_details.funding_org,
            f'{len(award_details.employees)} nominees',
            award_details.date_received
        ]) + '.pdf'
    else:
        raise ValueError('No award data provided')


def archive_file(old_path: str, new_path: str, processed_dir: str) -> None:
    new_path = os.path.join(processed_dir, new_path)
    if os.path.exists(new_path):
        base, ext = os.path.splitext(new_path)
        counter = 1
        while os.path.exists(new_path):
            new_path = f"{base}.{datetime.now().strftime('%y.%m.%d')}.{counter:03d}{ext}"
            counter += 1
    os.rename(old_path, new_path)


if __name__ == '__main__':
    pass
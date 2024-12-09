from constants import PAGE_COUNTS
from logger import SimpleLogger
from datetime import datetime
from pathlib import Path
from typing import Any
from modules import *
import fitz
import json
import os


LOGGER = SimpleLogger()


def load_serial_numbers(file_path: str) -> SerialNumbers:
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


def extract_pdf_info(pdf_path: str, fy: str, serial_numbers: SerialNumbers) -> PDFInfo:
    pdf_info = PDFInfo(
        file_name = os.path.basename(pdf_path),
        fiscal_year = fy,
    )
    with fitz.open(pdf_path) as doc:
        page_count: int = doc.page_count
        pdf_info.serial_number = serial_numbers.IND if page_count == PAGE_COUNTS.ind else serial_numbers.GRP
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


def export_as_TSV(tsv_path: str, award_data: IndAwd | GrpAwd) -> None:
    fields = [
        award_data.id,
        award_data.date_received,
        "", # date processed (empty)
        award_data.category,
        award_data.type,
        "", # name
        "", # monetary
        "", # hours
        "", # pay plan
        "", # org
        "", # supervisor
        award_data.nominator,
        award_data.funding_org,
        "", # MB div (empty)
        award_data.justification.text,
        award_data.value.title(),
        award_data.extent.title(),
        "",
    ]

    with open(tsv_path, 'a') as f:
        if award_data.category == 'IND':
            fields[5] = award_data.employee.name
            fields[6] = str(award_data.employee.monetary)
            fields[7] = str(award_data.employee.hours)
            fields[8] = award_data.employee.pay_plan
            fields[9] = award_data.employee.org
            fields[10] = award_data.employee.supervisor
            f.write("\t".join(fields) + '\n')
        elif award_data.category == 'GRP':
            for employee in award_data.employees:
                fields[5] = employee.name
                fields[6] = str(employee.monetary)
                fields[7] = str(employee.hours)
                fields[8] = employee.pay_plan
                fields[9] = employee.org
                fields[10] = employee.supervisor
                f.write("\t".join(fields) + '\n')


def export_as_txt(details_path: str, award_details: IndAwd | GrpAwd) -> None:
    with open(details_path, 'w') as f:
        f.write(str(award_details) + '\n')
        f.write(f'\n{"."*50}\n\n')


def insert_date_received(pdf_path: str, date_received: str) -> None:
    with fitz.open(pdf_path) as doc:
        for page in doc:
            date_field = [field for field in page.widgets() if field.field_name.lower() == 'date received']
            if len(date_field) == 1:
                date_xref = date_field[0].xref
                date_widget = page.load_widget(date_xref)
                date_widget.field_value = date_received
                date_widget.update()
                doc.saveIncr()


def save_serial_numbers(file_path: str, serial_numbers: SerialNumbers) -> None:
    with open(file_path, 'w') as file:
        json.dump(serial_numbers.__dict__, file, indent=4)


def generate_file_name(award_details: IndAwd | GrpAwd) -> str:
    if award_details.category == 'IND':
        return ' _ '.join([
            award_details.id,
            award_details.funding_org,
            award_details.employee.name,
            award_details.date_received
        ]) + '.pdf'

    elif award_details.category == 'GRP':
        return ' _ '.join([
            award_details.id,
            award_details.funding_org,
            f'{len(award_details.employees)} nominees',
            award_details.date_received
        ]) + '.pdf'
    else:
        raise ValueError('No award data provided')


def archive_file(old_path: Path, new_path: str, processed_dir: str) -> None:
    new_path = os.path.join(processed_dir, new_path)
    if os.path.exists(new_path):
        base, ext = os.path.splitext(new_path)
        counter = 1
        while os.path.exists(new_path):
            new_path = f"{base}.{datetime.now().strftime('%y.%m.%d')}.{counter:03d}{ext}"
            counter += 1
    os.rename(old_path, new_path)


def move_to_rejections(file_path: str, rejections_dir: str) -> None:
    new_path = os.path.join(rejections_dir, os.path.basename(file_path))
    os.rename(file_path, new_path)

if __name__ == '__main__':
    pass
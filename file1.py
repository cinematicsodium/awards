from configs.fields import PDF_FIELDS_CONFIG
from pprint import pprint
import fitz


def get_pdf_fields(file_path: str) -> dict:
    pdf_pages: dict = {}
    with fitz.open(file_path) as pdf:
        for page in pdf:
            for field in page.widgets():
                key = field.field_name.lower()
                value = field.field_value
                if not value:
                    continue
                pdf_pages[key] = value
    return pdf_pages

def determine_award_config(pdf_fields: tuple) -> str:
    pass

file_path = '/Users/Joey/Downloads/SAS Forms/FIELDS_CONFIG_MAX_14_VAR1.pdf'
pdf_fields = tuple(get_pdf_fields(file_path).keys())
print(f'{pdf_fields==PDF_FIELDS_CONFIG.IND=}')
print(f'{pdf_fields==PDF_FIELDS_CONFIG.MAX_14_VAR1=}')
print(f'{pdf_fields==PDF_FIELDS_CONFIG.MAX_14_VAR2=}')
print(f'{pdf_fields==PDF_FIELDS_CONFIG.MAX_21_VAR1=}')
print(f'{pdf_fields==PDF_FIELDS_CONFIG.MAX_21_VAR2=}')
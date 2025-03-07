from pathlib import Path

import fitz


def retrieve_forms() -> list[Path]:
    directory = Path("/Users/Joey/Downloads/SAS Forms")
    return [file for file in directory.iterdir() if file.is_file()]


def extract_form_fields(pdf_path: Path) -> dict[int, dict[str, str]]:
    with fitz.open(pdf_path) as pdf:
        form_fields_data: dict[int, list[str]] = {}
        for page in pdf:
            form_fields_data[page.number] = {}
            for field in page.widgets():
                key: str = str(field.field_name).lower().strip()
                value: str = str(field.field_value).strip()
                form_fields_data[page.number][key] = value
    return form_fields_data


if __name__ == "__main__":
    from pprint import pprint

    pdf_path = Path("/Users/Joey/Downloads/SAS Forms/FIELDS_CONFIG_IND.pdf")
    form_fields = extract_form_fields(pdf_path)
    pprint(form_fields, indent=4, width=132)

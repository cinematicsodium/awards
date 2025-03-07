from processing.extract import extract_form_fields, retrieve_forms

def main() -> None:
    forms = retrieve_forms()
    for form in forms:
        form_fields = extract_form_fields(form)



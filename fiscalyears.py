from modules import FiscalYear


FY2024 = FiscalYear(
    year                    = '2024',
    submissions_inbox       = r'/awards/2024/new submissions',
    serial_numbers_json     = r'/awards/2024/serial_numbers.json',
    award_details_TSV       = r'/awards/2024/tsv_file.txt',
    award_details_txt       = r'/awards/2024/award_details.txt',
    archived_items_folder   = r'/awards/2024/processed',
    rejected_items_folder   = r'/awards/2024/rejections',
)


FY2025 = FiscalYear(
    year                    = '2025',
    submissions_inbox       = r'/awards/2025/new submissions',
    serial_numbers_json     = r'/awards/2025/serial_numbers.json',
    award_details_TSV       = r'/awards/2025/tsv_file.txt',
    award_details_txt       = r'/awards/2025/award_details.txt',
    archived_items_folder   = r'/awards/2025/processed',
    rejected_items_folder   = r'/awards/2025/rejections',
)

FISCAL_YEARS: list[FiscalYear] = [
    FY2024,
    FY2025,
]


if __name__ == '__main__':
    pass
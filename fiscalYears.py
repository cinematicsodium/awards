from modules import FYInfo


FY2024 = FYInfo(
    year                    = '2024',
    submissions_inbox       = r'None',
    serial_numbers_json     = r'None',
    award_details_TSV       = r'None',
    award_details_txt       = r'None',
    archived_items_folder   = r'None',
    rejected_items_folder   = r'None',
)


FY2025 = FYInfo(
    year                    = '2025',
    submissions_inbox       = r'None',
    serial_numbers_json     = r'None',
    award_details_TSV       = r'None',
    award_details_txt       = r'None',
    archived_items_folder   = r'None',
    rejected_items_folder   = r'None',
)

FISCAL_YEARS: list[FYInfo] = [
    FY2024,
    FY2025,
]


if __name__ == '__main__':
    pass

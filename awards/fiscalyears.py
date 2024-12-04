from typing import NamedTuple
from icecream import ic
import os

class FiscalYear(NamedTuple):
    year: str
    new_submissions: str
    processed_folder: str
    serial_numbers: str
    TSV_file: str

FY2024 = FiscalYear(
    year                = '2024',
    new_submissions     =r'/Users/Joey/Library/Mobile Documents/com~apple~CloudDocs/Python/awards/2024/new submissions',
    processed_folder    =r'/Users/Joey/Library/Mobile Documents/com~apple~CloudDocs/Python/awards/2024/processed',
    serial_numbers      =r'/Users/Joey/Library/Mobile Documents/com~apple~CloudDocs/Python/awards/2024/serial_numbers.json',
    TSV_file            =r'/Users/Joey/Library/Mobile Documents/com~apple~CloudDocs/Python/awards/2024/tsv_file.txt'
)

FY2025 = FiscalYear(
    year                = '2025',
    new_submissions     =r'/Users/Joey/Library/Mobile Documents/com~apple~CloudDocs/Python/awards/2025/new submissions',
    processed_folder    =r'/Users/Joey/Library/Mobile Documents/com~apple~CloudDocs/Python/awards/2025/processed',
    serial_numbers      =r'/Users/Joey/Library/Mobile Documents/com~apple~CloudDocs/Python/awards/2025/serial_numbers.json',
    TSV_file            =r'/Users/Joey/Library/Mobile Documents/com~apple~CloudDocs/Python/awards/2025/tsv_file.txt'
)

FISCAL_YEARS: list[FiscalYear] = [
    FY2024,
    FY2025,
]


if __name__ == '__main__':
    pass
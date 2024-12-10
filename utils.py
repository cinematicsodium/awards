from winsound import Beep
from modules import EmpInfo
from pathlib import Path
from constants import (
    MONETARY_LIMITS,
    HOURS_LIMITS,
    VALUE_IDX_MAP,
    EXTENT_IDX_MAP
)
import re


def generate_id(file_path: str, fiscal_year: str, serial_number: int, grp=False) -> str:
    pattern = re.compile(r'\d{2}-(IND|GRP)-\d{3}')
    match = pattern.match(file_path)
    if match:
        return match.group()

    category = 'GRP' if grp else 'IND'
    return f'{fiscal_year[-2:]}-{category}-{str(serial_number).zfill(3)}'


def get_max_limits(value: str, extent: str) -> tuple[int, int]:
    value_idx = VALUE_IDX_MAP[value]
    extent_idx = EXTENT_IDX_MAP[extent]

    max_monetary = MONETARY_LIMITS[value_idx][extent_idx]
    max_hours = HOURS_LIMITS[value_idx][extent_idx]
    return max_monetary, max_hours


def is_compensation_valid(monetary: int, hours: int, max_monetary: int, max_hours: int):
    if monetary == 0 and hours == 0:
        raise ValueError('No monetary or time-off amounts found.')
    elif monetary % 1 != 0 or hours % 1 != 0:
        raise ValueError(f'Award amounts must be whole numbers: ${monetary:0,.2f}, {hours} hours')

    ratio = (monetary / max_monetary) + (hours / max_hours)
    return 0 < ratio <= 1.0


def play_alert() -> None:
    frequency_hz: int = 1000
    duration_ms: int = 500
    try:
        Beep(frequency_hz, duration_ms)
    except RuntimeError as e:
        print(e)


if __name__ == '__main__':
    play_alert()

from modules import EmpInfo
from constants import (
    MONETARY_LIMITS,
    HOURS_LIMITS,
    VALUE_IDX_MAP, 
    EXTENT_IDX_MAP
)


def generate_id(fy: str, sn: int, grp=False) -> str:
    category = 'GRP' if grp else 'IND'
    return f'{fy[-2:]}-{category}-{str(sn).zfill(3)}'


def get_max_limits(value: str, extent: str) -> tuple[int, int]:
    value_idx = VALUE_IDX_MAP[value]
    extent_idx = EXTENT_IDX_MAP[extent]
    max_monetary = MONETARY_LIMITS[value_idx][extent_idx]
    max_hours = HOURS_LIMITS[value_idx][extent_idx]
    return max_monetary, max_hours


def is_compensation_within_limits(monetary: int, hours: int, max_monetary: int, max_hours: int):
    ratio = (monetary / max_monetary) + (hours / max_hours)
    return 0 < ratio <= 1.0




if __name__ == '__main__':
    value = 'test1'
    extent = 'test2'
    max_monetary, max_hours = get_max_limits(value, extent)
    print(max_monetary, max_hours)
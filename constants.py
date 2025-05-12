from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from icecream import ic
from tabulate import tabulate

testing_mode: bool = False
status: str = "Enabled" if testing_mode is True else "Disabled"
monetary_hold: bool = True
input(
    f'\n\nTesting mode: {status}.\nMonetary hold: {monetary_hold}\n\nPress "Enter" to continue.\n\n'
).strip()

today = datetime.today()

if today.month >= 10:
    current_fiscal_year = today.year + 1
else:
    current_fiscal_year = today.year


_local_dir: Path = Path.cwd() / "awards"
_network_dir: Path = Path(
    r"X:\03 - Benefits & Work Life Balance\TEAM A\AWARDS\SPECIAL ACT OR SERVICE AWARDS"
)


class PathManager:
    file_archive_dir: Path = (
        _network_dir
        / f"FY {current_fiscal_year}\\Archive _ SASA Nomination Form Submissions"
    )
    field_name_data_path: Path = _local_dir / "field_name_data.json"
    json_archive_path: Path = _local_dir / "_output_JSON.json"
    logger_path: Path = _local_dir / "_logger.log"
    manual_entry_path: Path = _local_dir / "_manual_entry.yaml"
    serial_path: Path = _local_dir / "_serial_numbers.yaml"
    tracker_path: Path = Path(
        r"C:\Users\joseph.strong\OneDrive - US Department of Energy\FY 2025 _ Special Act Awards Log.xlsm"
    )
    tsv_output_path: Path = _local_dir / "_output_TSV.txt"

    def __init__(self):
        paths_list: list[Path] = [
            self.json_archive_path,
            self.logger_path,
            self.serial_path,
            self.tsv_output_path,
            self.file_archive_dir,
        ]
        for path in paths_list:
            if not path.exists():
                path.touch(exist_ok=True)


class AwardTracker:
    file_path: Path = PathManager.tracker_path
    sheet_name: str = "data_entry"
    ind_coord: str = "C2"
    grp_coord: str = "C3"


ORGANIZATION_DIVISIONS: dict[str, list[str]] = {
    "NA-1": ["NA-1.1", "NA-1.2", "NA-1.3"],
    "NA-10": [
        "NA-10.1",
        "NA-10.2",
        "NA-11",
        "NA-113",
        "NA-114",
        "NA-115",
        "NA-12",
        "NA-121",
        "NA-121.1",
        "NA-121.2",
        "NA-121.3",
        "NA-121.4",
        "NA-122",
        "NA-122.1",
        "NA-122.2",
        "NA-122.3",
        "NA-122.4",
        "NA-125",
        "NA-125.1",
        "NA-125.2",
        "NA-125.3",
        "NA-125.4",
        "NA-125.5",
        "NA-18",
        "NA-181",
        "NA-182",
        "NA-183",
        "NA-19",
        "NA-191",
        "NA-191.1",
        "NA-191.2",
        "NA-191.3",
        "NA-192",
        "NA-192.1",
        "NA-192.2",
        "NA-192.3",
        "NA-193",
        "NA-193.1",
    ],
    "NA-15": [
        "OST",
        "TRACOM",
        "AOCC",
        "AOEC",
        "AOWC",
        "NA-151",
        "NA-151.1",
        "NA-151.12",
        "NA-151.2",
        "NA-151.21",
        "NA-151.22",
        "NA-151.3",
        "NA-151.31",
        "NA-151.32",
        "NA-151.4",
        "NA-151.41",
        "NA-151.42",
        "NA-151.43",
        "NA-151.45",
        "NA-152",
        "NA-152.2",
        "NA-152.21",
        "NA-152.23",
        "NA-152.24",
        "NA-152.25",
        "NA-152.3",
        "NA-152.31",
        "NA-152.32",
        "NA-152.33",
        "NA-155",
        "NA-155.1",
        "NA-155.11",
        "NA-155.12",
        "NA-155.13",
        "NA-155.14",
        "NA-155.4",
        "NA-155.41",
        "NA-155.42",
        "NA-155.43",
        "NA-155.44",
        "NA-156",
        "NA-156.1",
        "NA-156.11",
        "NA-156.12",
        "NA-156.2",
    ],
    "NA-20": [
        "DNN",
        "NA-21",
        "NA-211",
        "NA-212",
        "NA-213",
        "NA-22",
        "NA-221",
        "NA-222",
        "NA-23",
        "NA-231",
        "NA-232",
        "NA-233",
        "NA-234",
        "NA-24",
        "NA-241",
        "NA-242",
        "NA-243",
        "NA-244",
    ],
    "NA-30": ["NRLFO", "NR"],
    "NA-40": ["NA-41", "NA-43", "NA-44"],
    "NA-70": [
        "NA-71",
        "NA-711",
        "NA-712",
        "NA-713",
        "NA-74",
        "NA-743",
        "NA-744",
        "NA-745",
        "NA-746",
        "NA-77",
        "NA-771",
    ],
    "NA-80": ["NA-81", "NA-82", "NA-83", "NA-84"],
    "NA-90": [
        "NA-90.1",
        "NA-90.2",
        "NA-91",
        "NA-91.1",
        "NA-91.2",
        "NA-91.3",
        "NA-91.4",
        "NA-91.5",
        "NA-92",
        "NA-92.1",
        "NA-92.2",
        "NA-92.3",
        "NA-93",
        "NA-94",
    ],
    "NA-CI": ["NA-CI-1", "NA-CI-10", "NA-CI-30"],
    "NA-COMM": ["NA-COMM"],
    "NA-ESH": [
        "NA-ESH-1.1",
        "NA-ESH-10",
        "NA-ESH-11",
        "NA-ESH-12",
        "NA-ESH-13",
        "NA-ESH-14",
        "NA-ESH-15",
        "NA-ESH-20",
        "NA-ESH-21",
        "NA-ESH-22",
        "NA-ESH-23",
        "NA-ESH-24",
    ],
    "NA-GC": ["NA-GC-10", "NA-GC-30"],
    "NA-IM": ["NA-IM-1", "NA-IM-10", "NA-IM-11", "NA-IM-12", "NA-IM-20"],
    "NA-KC (KCFO)": ["KCFO", "NA-KC", "KANSAS CITY"],
    "NA-LA (LAFO)": ["LAFO", "NA-LA", "LOS ALAMOS"],
    "NA-LL (LFO)": ["LFO", "NA-LL", "LIVERMORE"],
    "NA-MB": [
        "NA-MB-1",
        "NA-MB-1.1",
        "NA-MB-1.4",
        "NA-MB-10",
        "NA-MB-10.1",
        "NA-MB-16",
        "NA-MB-17",
        "NA-MB-18",
        "NA-MB-19",
        "NA-MB-20",
        "NA-MB-21",
        "NA-MB-23",
        "NA-MB-40",
        "NA-MB-41",
        "NA-MB-42",
        "NA-MB-50",
        "NA-MB-53",
        "NA-MB-55",
        "NA-MB-56",
        "NA-MB-60",
        "NA-MB-62",
        "NA-MB-63",
        "NA-MB-64",
        "NA-MB-70",
        "NA-MB-80",
        "NA-MB-81",
        "NA-MB-811",
        "NA-MB-812",
        "NA-MB-813",
        "NA-MB-82",
        "NA-MB-83",
        "NA-MB-90",
        "NA-MB-91",
        "NA-MB-92",
        "NA-MB-921",
        "NA-MB-922",
    ],
    "NA-NV (NFO)": ["NA-NV", "NFO"],
    "NA-PAS": [
        "NA-PAS-1.1",
        "NA-PAS-1.2",
        "NA-PAS-10",
        "NA-PAS-11",
        "NA-PAS-111",
        "NA-PAS-112",
        "NA-PAS-113",
        "NA-PAS-20",
        "NA-PAS-21",
        "NA-PAS-211",
        "NA-PAS-212",
        "NA-PAS-213",
        "NA-PAS-30",
        "NA-PAS-31",
        "NA-PAS-311",
        "NA-PAS-312",
        "NA-PAS-313",
        "NA-PAS-314",
    ],
    "NA-PFO": [f"NA-PFO-1"] + [f"NA-PFO-{i}" for i in range(10, 101, 10)],
    "NA-SN (SFO)": ["NA-SN", "SANDIA", "SFO"],
    "NA-SV (SRFO)": ["NA-SV", "SAVANNAH", "SRFO"],
    "NA-YFO": [
        "YFO",
        "NA-YFO",
        "NA-YFO-01",
        "NA-YFO-10",
        "NA-YFO-20",
        "NA-YFO-40",
        "NA-YFO-50",
        "NA-YFO-60",
    ],
}

mb_map: dict[str, list[str]] = {
    "MB-10": ["MB-10.1", "MB-16", "MB-17", "MB-18", "MB-19"],
    "MB-1": ["MB-1"],
    "MB-1.1": ["MB-1.1"],
    "MB-1.4": ["MB-1.4"],
    "MB-20": ["MB-21", "MB-23"],
    "MB-40": ["MB-41", "MB-42"],
    "MB-50": ["MB-53", "MB-55", "MB-56"],
    "MB-60": ["MB-62", "MB-63", "MB-64"],
    "MB-70": ["MB-70"],
    "MB-80": ["MB-81", "MB-811", "MB-812", "MB-813", "MB-82", "MB-83"],
    "MB-90": ["MB-91", "MB-92", "MB-921", "MB-922"],
}

CONSULTANT_MAP: dict[str, str] = {
    "NA-10": "Gus",
    "NA-15": "Gus",
    "NA-1": "Gus",
    "NA-20": "Gus",
    "NA-30": "Joy",
    "NA-40": "Gus",
    "NA-70": "Gus",
    "NA-80": "Joy",
    "NA-90": "Gus",
    "NA-CI": "Gus",
    "NA-COMM": "Joy",
    "NA-ESH": "Gus",
    "NA-GC": "Joy",
    "NA-IM": "Joy",
    "NA-KC (KCFO)": "Joy",
    "NA-LA (LAFO)": "Joy",
    "NA-LL (LFO)": "Joy",
    "NA-MB": "Joy",
    "NA-PFO": "Joy",
    "NA-YFO": "Joy",
    "NA-NV (NFO)": "Joy",
    "NA-PAS": "Joy",
    "NA-SN (SFO)": "Joy",
    "NA-SV (SRFO)": "Joy",
}

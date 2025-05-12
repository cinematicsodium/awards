import json
import re
import warnings
from datetime import date, datetime, timedelta
from time import sleep
from typing import Optional
from uuid import uuid4

import openpyxl
import yaml

from formatting.formatter import Formatter

from .constants import (
    CONSULTANT_MAP,
    AwardTracker,
    PathManager,
    current_fiscal_year,
    division_structure,
    mb_map,
    testing_mode,
)
from .logger import Logger

logger = Logger()
formatter = Formatter()


class IDManager:
    @staticmethod
    def load_SN_data() -> dict[str, int]:
        try:
            if not PathManager.serial_path.exists():
                raise ValueError(f"Log ID file not found: {PathManager.serial_path}")

            with open(PathManager.serial_path, "r") as file:

                sn_data: dict[str, int] = yaml.safe_load(file)

                if not sn_data:
                    raise ValueError("Log ID data not found in YAML file.")
                elif not all(
                    [
                        isinstance(sn_data, dict),
                        all(isinstance(k, str) for k in sn_data.keys()),
                        all(isinstance(v, int) for v in sn_data.values()),
                    ]
                ):
                    raise ValueError(
                        "Log ID data is not in the expected dictionary format."
                    )
            return sn_data
        except Exception as e:
            raise ValueError(f"Unable to load Log ID data. {e}")

    @staticmethod
    def load_archive() -> dict[str, dict[str, str | int | None]]:
        try:
            with open(PathManager.json_archive_path, "r", encoding="utf-8") as file:
                content: str = file.read().strip()
                content = r"{}" if not content else content
                json_data: dict[str, dict[str, str | int | None]] = json.loads(content)
            return json_data
        except Exception as e:
            raise ValueError(
                f"Unable to load archived JSON data from {PathManager.json_archive_path.name}. {e}"
            )

    @staticmethod
    def get(category: str) -> int:
        """
        Retrieves the log ID from the JSON file formatted as {fiscal_year}-{category}-{serial_number}.
        """
        if testing_mode:
            return str(uuid4())

        archive_data = IDManager.load_archive()
        SN_data = IDManager.load_SN_data()
        fy_str: str = str(current_fiscal_year)[-2:]
        target_ser_num = SN_data.get(str(category))
        if target_ser_num is None:
            raise ValueError(f"Data not found for category: {category}")
        while True:
            log_id: str = f"{fy_str}-{category}-{str(target_ser_num).zfill(3)}"
            if archive_data.get(log_id) is None:
                break
            else:
                logger.warning(f"Duplicate found for {log_id}")
                target_ser_num += 1

        if target_ser_num != SN_data[category]:
            IDManager.update(category=category, new_value=target_ser_num)

        return log_id

    @staticmethod
    def update(category: str, new_value: Optional[int] = None) -> None:
        if testing_mode:
            return

        serial_numbers = IDManager.load_SN_data()
        if new_value is None:
            serial_numbers[category] += 1
        else:
            serial_numbers[category] = new_value

        with open(PathManager.serial_path, "w") as file:
            yaml.safe_dump(serial_numbers, file, indent=4, sort_keys=False)


def find_organization(input_org: str) -> tuple[Optional[str], Optional[str]]:
    def is_org_match(fmt_org: str, field: Optional[str], fmt_input: str) -> bool:
        org_conditions_met: bool = any([fmt_org in fmt_input, fmt_input in fmt_org])
        field_conditions_met: bool = False
        if isinstance(field, str):
            field = re.sub(r"[\(\)]+", "", field).lower()
            field_conditions_met = bool(field in fmt_input)
        return any([org_conditions_met, field_conditions_met])

    def is_div_match(fmt_div: str, fmt_input: str) -> bool:
        return any([fmt_div in fmt_input, fmt_input in fmt_div])

    """
    Finds the organization matching the input string.
    """
    org_match: Optional[str] = None
    div_match: Optional[str] = None

    if not input_org:
        return (org_match, div_match)

    formatted_input = formatter.standardized_org_div(input_org)

    for target_org, div_list in division_structure.items():
        field: Optional[str] = None
        formatted_org: str = formatter.standardized_org_div(target_org)
        if len(formatted_org.split(" ")) == 2:
            formatted_org, field = (part.strip() for part in formatted_org.split(" "))
        if org_match is None and is_org_match(formatted_org, field, formatted_input):
            org_match = target_org

        div_list = list(reversed(div_list))
        for target_div in div_list:
            formatted_div = formatter.standardized_org_div(target_div)
            if div_match is None and is_div_match(formatted_div, formatted_input):
                org_match = target_org
                div_match = target_div

        if org_match and div_match:
            break

    return org_match, div_match


def find_mgmt_division(input_org: str) -> str:
    if not input_org:
        return

    formatted_input = Formatter(input_org).standardized_org_div()

    for org, div_list in mb_map.items():
        formatted_org = Formatter(org).standardized_org_div()

        if formatted_org in formatted_input:
            return org

        for div in div_list:
            formatted_div = Formatter(div).standardized_org_div()

            if formatted_div in formatted_input:
                return org
    return None


def update_serial_numbers():

    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

    try:
        path = AwardTracker.file_path.absolute()
        wb = openpyxl.load_workbook(path, data_only=True)
        sheet = wb[AwardTracker.sheet_name]
        xl_ind_val: int = int(sheet[AwardTracker.ind_coord].value[-3:])
        xl_grp_val: int = int(sheet[AwardTracker.grp_coord].value[-3:])

        with open(PathManager.serial_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            yaml_ind_val = data["IND"]
            yaml_grp_val = data["GRP"]

        yaml_ind_val = xl_ind_val if xl_ind_val > yaml_ind_val else yaml_ind_val
        yaml_grp_val = xl_grp_val if xl_grp_val > yaml_grp_val else yaml_grp_val

        with open(PathManager.serial_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(data, file, indent=4, sort_keys=False, encoding="utf-8")

            print(
                f"\n"
                "Updated serial_numbers.yaml\n"
                f"IND: {yaml_ind_val}\n"
                f"GRP: {yaml_grp_val}\n"
            )

    except Exception as e:
        print(f"Unable to update serial_numbers.yaml. {e}")

    warnings.resetwarnings()
    sleep(3)


class ManualEntry:
    @staticmethod
    def load() -> dict[str, str]:
        with open(PathManager.manual_entry_path, "r") as file:
            try:
                data: dict = yaml.safe_load(file)
                return {k: Formatter(v).value() for k, v in data.items()}
            except Exception as e:
                print(e)

    @staticmethod
    def reset():
        keys: list[str] = [
            "employee_name",
            "employee_pay_plan",
            "employee_org",
            "sas_monetary_amount",
            "sas_time_off_amount",
            "ots_monetary_amount",
            "ots_time_off_amount",
            "nominator_name",
            "nominator_org",
            "funding_string",
            "certifier_name",
            "certifier_org",
            "employee_supervisor_name",
            "employee_supervisor_org",
            "approver_name",
            "approver_org",
            "reviewer_name",
            "value",
            "extent",
            "justification",
            "date_received",
        ]

        try:
            with open(PathManager.manual_entry_path, "w") as file:
                [file.write(f"{k}:\n") for k in keys]
            print(f"{PathManager.manual_entry_path.name} reset.")
        except Exception as e:
            print(e)


def clean_JSON_output():
    import json

    try:
        with open(PathManager.json_archive_path, "r", encoding="utf-8") as jfile:
            json_data: dict[str, dict[str | int | None]] = json.load(jfile)
            initial_count: int = len(json_data)

            keys = [key for key in json_data if len(key) > 10]
            for key in keys:
                json_data.pop(key)

        final_count: int = len(json_data)

        items_removed: int = initial_count - final_count

        with open(PathManager.json_archive_path, "w", encoding="utf-8") as jfile:
            json.dump(json_data, jfile, indent=4, sort_keys=False)
            print(
                f"\ninitial count: {initial_count}\n"
                f"items removed: {items_removed}\n"
                f"final count: {final_count}"
            )
    except Exception as e:
        print(e)


class DateHandler:
    current_fy: int = 2025
    fy_end_date = datetime(current_fy, 9, 30)
    next_fy = current_fy + 1

    @staticmethod
    def convert_to_str(date_str: datetime) -> Optional[str]:
        try:
            return date_str.strftime("%Y-%m-%d")
        except:
            print(f"Unable to convert '{date_str} to datetime'")

    @staticmethod
    def convert_to_datetime(input_date: str | date) -> datetime:
        if not input_date:
            return

        elif isinstance(input_date, date):
            return datetime(input_date.year, input_date.month, input_date.day)

        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m-%d-%Y",
            "%m/%d/%Y",
            "%m/%d/%y",
            "%m-%d",
            "%m/%d",
        ]
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(input_date, fmt)

                if "%y" not in fmt.lower():
                    parsed_date = parsed_date.replace(year=datetime.now().year)
                return parsed_date.replace(second=0, microsecond=0)
            except ValueError:
                continue
        raise ValueError(f"Date format not recognized for: {input_date}")

    @staticmethod
    def _compare_dates(start_date: datetime, end_date: datetime) -> None:
        if start_date >= end_date:
            raise ValueError(
                f"Invalid date range. Start date must be before the end date.\n"
                f"start_date: {start_date}\n"
                f"end_date: {end_date}\n"
                f"timedelta: {(end_date-start_date).days} days"
            )

    @staticmethod
    def validate_duration(start_date: datetime, end_date: datetime) -> None:
        DateHandler._compare_dates(start_date, end_date)
        min_detail_days = timedelta(days=90)
        max_detail_days = timedelta(days=365)
        actual_duration = end_date - start_date
        if min_detail_days <= actual_duration <= max_detail_days:
            return
        else:
            error_message = f"Invalid Detail duration: {actual_duration.days} days.\nMinimum: 90\nMaximum: 365"
            raise ValueError(error_message)

    @staticmethod
    def calculate_deadline(start_date: datetime) -> datetime:
        deadline = start_date + timedelta(days=30)
        return deadline


class Archive:
    data: dict[str, dict[str, str]] = {}
    sorted_data: dict[str, dict[str, str]] = {}
    hrc: Optional[str] = None

    def __init__(self):
        self.load()
        self.select_hrc()
        print(self.hrc)

    def get_user_option_selection(self, msg: str, options: list[str] | set[str]):
        options_dict: dict[int:str] = {
            idx: option for idx, option in enumerate(options)
        }
        print(msg)
        [print(f"{i + 1}: {opt}") for i, opt in options_dict.items()]
        while True:
            try:
                selection: str = input("> ").strip()
                if selection == "":
                    return
                else:
                    return options_dict[int(selection) - 1]
            except Exception as e:
                print(f"Invalid selection. {e}")

    def select_hrc(self):
        msg = "Select an HR Consultant or press 'Enter' to continue."
        hrc_options = set(CONSULTANT_MAP.values())
        self.hrc = self.get_user_option_selection(msg, hrc_options)

    def select_log_id(self):
        while True:
            print("Enter a Log ID.")
            log_id: str = input("> ").strip()
            id_data = self.data.get(log_id)
            if id_data:
                self.sorted_data = self.data[id_data]

    def get_date_received(self):
        while True:
            try:
                print("Enter date received.")
                date_received = input("> ").strip()
                date_received = DateHandler.convert_to_datetime(date_received)
                date_received = DateHandler.convert_to_str(date_received)
                self.sorted_data["date_received"] = date_received
            except Exception as e:
                print(f"Invalid input. {e}")

    def load(self):
        with open(PathManager.json_archive_path, "r", encoding="utf-8") as jf:
            self.data = json.load(jf)


if __name__ == "__main__":
    Archive()

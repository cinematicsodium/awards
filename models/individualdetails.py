import json
import shutil
import warnings
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import fitz
from rich.console import Console
from tabulate import tabulate

from constants import (
    CONSULTANT_MAP,
    EvalManager,
    PathManager,
    monetary_hold,
    testing_mode,
)
from .evaluator import AwardEvaluator
from .formatterclass import Formatter
from .logger import Logger
from .utils import IDManager, ManualEntry, find_mgmt_division, find_organization

console = Console()
logger = Logger()


@dataclass
class BaseProcessor:
    source_path: Optional[Path | str] = None

    def __post_init__(self):
        self.handle_source_path()
        self.log_id: Optional[str] = None
        self.funding_org: Optional[str] = None
        self.nominator_name: Optional[str] = None
        self.nominator_org: Optional[str] = None
        self.funding_string: Optional[str] = None
        self.certifier_name: Optional[str] = None
        self.certifier_org: Optional[str] = None
        self.approver_name: Optional[str] = None
        self.approver_org: Optional[str] = None
        self.mb_division: Optional[str] = None
        self.justification: Optional[str] = None
        self.value: Optional[str] = None
        self.extent: Optional[str] = None
        self.category: Optional[str] = None
        self.type: Optional[str] = None
        self.date_received = datetime.now().strftime("%Y-%m-%d")
        self.consultant: Optional[str] = None

    def handle_source_path(self) -> None:
        """Validates and processes the source path."""
        source_path = (
            self.source_path.name
            if isinstance(self.source_path, Path)
            else self.source_path
        )
        logger.path(source_path)

        if self.source_path is None:
            return
        if isinstance(self.source_path, str):
            try:
                self.source_path = Path(self.source_path.replace('"', "").strip())
            except:
                raise ValueError(
                    f"Unable to convert '{self.source_path}' to a Path object."
                )
        if not isinstance(self.source_path, Path):
            raise ValueError(
                "Invalid source path type.\n"
                "Expected: [Path, str, None]\n"
                f"Received: {type(self.source_path)}"
            )
        if not self.source_path.is_file() or not self.source_path.exists():
            raise ValueError(f"Source path is not a file or does not exist.")

    def extract_pdf_data(self) -> dict[str, Optional[str]]:

        warnings.filterwarnings("ignore", module="pymupdf")

        pdf_data = {}

        with fitz.open(self.source_path) as doc:
            if doc.page_count > 2:
                raise ValueError("IndProcessor is unable to process GRP awards.")
            for page in doc:
                for field in page.widgets():
                    key = Formatter(field.field_name).key()
                    val = Formatter(field.field_value).value()
                    pdf_data[key] = val

        if not pdf_data:
            raise ValueError("No data extracted from the PDF.")
        logger.info(f"Extracted {len(pdf_data)} items from PDF.")
        warnings.resetwarnings()

        return pdf_data


@dataclass
class IndProcessor(BaseProcessor):
    def __post_init__(self):
        super().__post_init__()
        self.log_id = None
        self.funding_org = None
        self.funding_string = None
        self.monetary_amount = None
        self.time_off_amount = None
        self.employee_name = None
        self.employee_org = None
        self.employee_pay_plan = None
        self.employee_supervisor_name = None
        self.employee_supervisor_org = None
        self.nominator_name = None
        self.nominator_org = None
        self.value = None
        self.extent = None
        self.justification = None
        self.category = None
        self.type = None
        self.consultant = None

    def attributes(self) -> dict[str, str | None]:
        monetary_amount = (
            f"${self.monetary_amount}" if self.monetary_amount is not None else None
        )
        time_off_amount = (
            f"{self.time_off_amount} hours"
            if self.time_off_amount is not None
            else None
        )
        justification = (
            f"{len(self.justification.split(' '))} words"
            if self.justification
            else None
        )
        attributes: dict[str, str | None] = {
            "Source": self.source_path.name if self.source_path else None,
            "Log ID": self.log_id,
            "Funding Org": self.funding_org,
            "Funding String": self.funding_string,
            "Monetary Amount": monetary_amount,
            "Time-Off Amount": time_off_amount,
            "Employee Name": self.employee_name,
            "Employee Org": self.employee_org,
            "Employee Pay Plan": self.employee_pay_plan,
            "Employee Supervisor Name": self.employee_supervisor_name,
            "Employee Supervisor Org": self.employee_supervisor_org,
            "Nominator Name": self.nominator_name,
            "Nominator Org": self.nominator_org,
            "Value": self.value,
            "Extent": self.extent,
            "Justification": justification,
            "Category": self.category,
            "Type": self.type,
            "Date Received": self.date_received,
            "HRC": self.consultant,
        }
        return attributes

    def __str__(self):
        return "\n".join(f"{k}: {v}" for k, v in self.attributes().items())

    def _table(self):
        rows = [[f"{k}:", v if v else "-"] for k, v in self.attributes().items()]
        table = tabulate(rows, tablefmt="simple_outline")
        return table

    def key_filter(self, field1: str, field2: str, pdf_data: dict):
        return field1 if field1 in pdf_data else field2 if field2 in pdf_data else None

    def populate_attributes(self, pdf_data: dict[str, Optional[str]]):
        """Populates attributes from PDF data."""
        category = "IND"
        self.log_id = IDManager.get(category)

        self.employee_name = Formatter(pdf_data.get("employee_name")).name()
        self.employee_org = pdf_data.get("organization")

        key = self.key_filter("pay_plan_gradestep_1", "pay_plan_gradestep", pdf_data)
        self.employee_pay_plan = Formatter(pdf_data.get(key)).pay_plan()

        key = self.key_filter("undefined", "amount", pdf_data)
        self.sas_monetary_amount = Formatter(pdf_data.get(key)).numerical()

        key = self.key_filter("hours_2", "hours", pdf_data)
        self.sas_time_off_amount = Formatter(pdf_data.get(key)).numerical()

        key = self.key_filter("on_the_spot_award", "amount_2", pdf_data)
        self.ots_monetary_amount = Formatter(pdf_data.get(key)).numerical()

        key = self.key_filter("hours", "hours_2", pdf_data)
        if pdf_data.get("undefined_2") is not None:
            key = "undefined_2"
        self.ots_time_off_amount = Formatter(pdf_data.get(key)).numerical()

        key = self.key_filter("please_print", "nominators_name", pdf_data)
        self.nominator_name = Formatter(pdf_data.get(key)).name()

        key = self.key_filter("org", "organization_2", pdf_data)
        self.nominator_org = pdf_data.get(key)

        key = self.key_filter(
            "please_print_2", "a_nominees_team_leadersupervisor_1", pdf_data
        )
        self.employee_supervisor_name = Formatter(pdf_data.get(key)).name()

        key = self.key_filter("org_3", "organization_3", pdf_data)
        self.employee_supervisor_org = pdf_data.get(key)

        key = "special_act_award_funding_string_2"
        self.certifier_name = Formatter(pdf_data.get(key)).name()

        self.certifier_org = pdf_data.get("org_2")

        key = self.key_filter(
            "please_print_3", "approving_officialdesignee_1", pdf_data
        )
        self.approver_name = Formatter(pdf_data.get(key)).name()

        key = self.key_filter("org_4", "organization_5", pdf_data)
        self.approver_org = pdf_data.get(key)

        self.funding_string = pdf_data.get("special_act_award_funding_string_1")

        key = self.key_filter(
            "extent_of_application",
            "extent_of_application_limited_extended_or_general",
            pdf_data,
        )
        self.justification = Formatter(pdf_data.get(key)).justification()

        self.set_value_and_extent(pdf_data)
        self.handle_external_pdf(pdf_data)
        self.category = category

        logger.info("Populated attributes from PDF data.")

    def handle_external_pdf(self, pdf_data: dict[str, Optional[str]]) -> None:
        """Normalizes PDF data from external agencies."""

        if "employee's_name" not in pdf_data:
            return

        self.employee_name = Formatter(pdf_data.get("employee's_name")).name()
        self.employee_pay_plan = Formatter(
            pdf_data.get("position_title_series_and_grade")
        ).pay_plan()
        self.sas_monetary_amount = Formatter(
            pdf_data.get("special_act_amount_first_page")
        ).numerical()
        self.ots_monetary_amount = Formatter(
            pdf_data.get("on_the_spot_amount_first_page")
        ).numerical()

        time_off_field = pdf_data.get("hours_first_page")
        if (
            str(pdf_data.get("on-the-spot_award_checkbox")).lower() == "yes"
            or self.ots_monetary_amount
        ):
            self.ots_time_off_amount = time_off_field
        else:
            self.sas_time_off_amount = time_off_field

        sas_justif_field = pdf_data.get("section_1_justification", "")
        ots_justif_field = pdf_data.get("section_1_ots_justification", "")
        justification_text = (
            sas_justif_field
            if len(sas_justif_field) > len(ots_justif_field)
            else ots_justif_field
        )

        self.justification = Formatter(justification_text).justification()
        self.funding_org = "DOE"
        self.nominator_name = "--"
        self.employee_supervisor_name = "--"
        self.approver_name = "--"

        logger.info("Normalized PDF data from an external organization.")

    def set_value_and_extent(self, pdf_data: dict[str, Optional[str]]) -> None:
        """Sets value and extent attributes based on PDF data options."""
        value_options: list[str] = [
            k
            for k, v in pdf_data.items()
            if str(k).lower() in EvalManager.value_options and str(v).lower() == "on"
        ]
        self.value = value_options[0] if len(value_options) == 1 else None

        extent_options: list[str] = [
            k.capitalize()
            for k, v in pdf_data.items()
            if str(k).capitalize() in EvalManager.extent_options
            and str(v).lower() == "on"
        ]
        self.extent = extent_options[0] if len(extent_options) == 1 else None

        logger.info("Set value and extent attributes from PDF data.")

    def _validate_pay_plan(self):
        """Validates the employee's pay plan name, disallowing 'ES' pay plans."""
        if not self.employee_pay_plan:
            return

        if "es" in str(self.employee_pay_plan).lower():
            raise ValueError(f"'ES' pay plans not allowed: {self.employee_pay_plan}")
        logger.info("Validated employee pay plan.")

    def _get_missing_fields(self):
        """Identifies missing required fields in the dictionary."""
        required_fields: dict[str, str] = {
            "employee_name": self.employee_name,
            "nominator_name": self.nominator_name,
            "employee_supervisor_name": self.employee_supervisor_name,
            "approver_name": self.approver_name,
            "justification": self.justification,
        }
        return [k for k, v in required_fields.items() if v is None]

    def _prompt_user_action(self, error_msg: str):
        logger.warning(error_msg)

        options = {1: "Continue", 9: "Skip"}
        while True:
            try:
                logger.warning(
                    "Make a selection:\n"
                    "1: Continue processing.\n"
                    "9: Skip this award."
                )
                selection: int = int(input("> ").strip())
                if selection not in options:
                    raise ValueError("Selection must be 1 or 9.")
                break
            except Exception as e:
                logger.error(f"Invalid selection. {e}")
        if selection == 9:
            raise ValueError(f"Unable to proceed with processing. {error_msg}")

    def _validate_fields(self) -> list[str]:
        """Validates form fields and prompts user for missing information."""
        missing_fields: list[str] = self._get_missing_fields()
        if missing_fields:
            error_msg: str = f"Missing Fields:\n{missing_fields}".strip()
            self._prompt_user_action(error_msg)
        self._validate_pay_plan()
        logger.info("Validated form fields and handled missing fields.")

    def _parse_org_divs(self) -> None:
        """Parses and determines organizational divisions for employee-related entities."""
        org_matches: list[str] = []

        org_match, div_match = find_organization(self.employee_org)
        self.employee_org = div_match if div_match else org_match if org_match else None

        org_match, div_match = find_organization(
            self.employee_supervisor_org
        )  # 'NA-SN (Deputy Field Office Manager)'
        self.employee_supervisor_org = (
            div_match if div_match else org_match if org_match else None
        )

        org_match, div_match = find_organization(self.nominator_org)
        self.nominator_org = (
            div_match if div_match else org_match if org_match else None
        )
        if org_match:
            org_matches.append(org_match)

        org_match, div_match = find_organization(self.certifier_org)
        self.certifier_org = (
            div_match if div_match else org_match if org_match else None
        )
        if org_match:
            org_matches.append(org_match)

        org_match, div_match = find_organization(self.approver_org)
        self.approver_org = div_match if div_match else org_match if org_match else None
        if org_match:
            org_matches.append(org_match)

        if not self.funding_org:
            self._determine_funding_organization(org_matches)
        self._set_consultant()
        if org_matches:
            mb_orgs: list[str] = [
                org for org in org_matches if "mb" in str(org).lower()
            ]
            if mb_orgs:
                self._set_mb_division(mb_orgs)
        logger.info("Parsed organizational divisions.")

    def _determine_funding_organization(self, org_matches: list[str]) -> None:
        """Determines the most frequent funding organization from a list of matches."""
        if not org_matches:
            raise ValueError("Unable to determine funding org.")

        org_counter = Counter(org_matches).most_common()
        self.funding_org = org_counter[0][0]

        if self.funding_org is None:
            raise ValueError("Unable to determine funding org.")
        logger.info("Determined funding organization.")

    def _set_consultant(self) -> None:
        """Set the consultant based on the funding organization."""
        self.consultant = CONSULTANT_MAP.get(self.funding_org)
        if self.consultant is None:
            logger.warning(f"No consultant found for funding org '{self.funding_org}'")
        logger.info("Consultant set for funding organization.")

    def _set_mb_division(self, mb_orgs: list[str]) -> None:
        """Set the MB division if the funding organization contains 'mb'."""

        mb_div_list = []
        for org in mb_orgs:
            div_match = find_mgmt_division(org)
            mb_div_list.append(div_match) if div_match else None

        if mb_div_list:
            self.mb_division = Counter(mb_div_list).most_common()[0][0]

            if not self.mb_division:
                logger.warning(
                    f"Unable to determine MB orgs based on the following: {mb_orgs}"
                )
            else:
                logger.info(f"MB division set to '{self.mb_division}'")

    def _classify_amounts(self):
        """
        Categorizes award amounts as either SAS or OTS based on specific fields.
        """
        if self.sas_monetary_amount or self.sas_time_off_amount:
            self.monetary_amount = self.sas_monetary_amount
            self.time_off_amount = self.sas_time_off_amount

        elif self.ots_monetary_amount or self.ots_time_off_amount:
            self.type = "OTS"
            self.monetary_amount = self.ots_monetary_amount
            self.time_off_amount = self.ots_time_off_amount

        self.type = self.type if self.type else "SAS"
        self.monetary_amount = self.monetary_amount if self.monetary_amount else 0
        self.time_off_amount = self.time_off_amount if self.time_off_amount else 0

        logger.info(f"Type set to {self.type}.")

    def _validate_amounts(self):
        """
        Confirms the award amounts meet the required criteria.
        """
        if self.monetary_amount == 0 and self.time_off_amount == 0:
            raise ValueError("No monetary or time-off amounts found.")

        elif any(
            [
                self.monetary_amount != int(self.monetary_amount),
                self.time_off_amount != int(self.time_off_amount),
            ]
        ):
            raise ValueError(
                "Amounts awarded must be integers.\n"
                f"Monetary: {self.monetary_amount}\n"
                f"Time-Off: {self.time_off_amount}"
            )
        self.monetary_amount = int(self.monetary_amount)
        self.time_off_amount = int(self.time_off_amount)

        if any(
            [
                self.monetary_amount < 0,
                self.time_off_amount < 0,
            ]
        ):
            raise ValueError(
                "Amounts awarded must be positive.\n"
                f"Monetary: '{self.monetary_amount}'\n"
                f"Time-Off: '{self.time_off_amount}'"
            )

        if self.monetary_amount and monetary_hold is True:
            raise ValueError(
                "Unable to process monetary awards at this time.\n"
                f"monetary amount: {self.monetary_amount}\n"
                f"time-off amount: {self.time_off_amount}"
            )
        logger.info("Award amounts meet the required criteria for further processing.")

        try:
            evaluator = AwardEvaluator(
                self.value, self.extent, self.monetary_amount, self.time_off_amount
            )
            eval_results = evaluator.evaluate()
            logger.info(eval_results)
        except SyntaxError as se:
            logger.warning(se)

    def _validate_and_transform(self) -> None:
        self._validate_fields()
        self._parse_org_divs()
        self._classify_amounts()
        self._validate_amounts()

    def _save_json(self) -> None:
        """
        Saves all award data to a JSON file.
        """
        attributes: dict[str, str | int | None] = {
            "source_path": self.source_path.name if self.source_path else None,
            "log_id": self.log_id,
            "funding_org": self.funding_org,
            "funding_string": self.funding_string,
            "monetary_amount": self.monetary_amount,
            "time_off_amount": self.time_off_amount,
            "employee_name": self.employee_name,
            "employee_org": self.employee_org,
            "employee_pay_plan": self.employee_pay_plan,
            "employee_supervisor_name": self.employee_supervisor_name,
            "employee_supervisor_org": self.employee_supervisor_org,
            "nominator_name": self.nominator_name,
            "nominator_org": self.nominator_org,
            "approver_name": self.approver_name,
            "approver_org": self.approver_org,
            "certifier_name": self.certifier_name,
            "certifier_org": self.certifier_org,
            "value": self.value,
            "extent": self.extent,
            "justification": f"{len(self.justification.split(' '))} words",
            "category": self.category,
            "type": self.type,
            "date_received": self.date_received,
            "consultant": self.consultant,
        }

        for k, v in attributes.items():
            if v is None or type(v) in [str, int, float]:
                pass
            else:
                v = str(v)
            attributes[k] = v
        
        with open(PathManager.json_archive_path, "r", encoding="utf-8") as file:
            content: str = file.read().strip()
            content = "[]" if not content else content
            json_data: dict[str, dict[str, str | int | None]] = json.loads(content)
        json_data[attributes["log_id"]] = attributes

        with open(PathManager.json_archive_path, "w", encoding="utf-8") as file:
            json.dump(json_data, file, indent=4, sort_keys=False)

        logger.info(f"'{PathManager.json_archive_path.name}' updated with new data")

    def _save_tsv(self) -> None:
        """Saves data in TSV format to a file."""
        self.mb_division = self.mb_division if self.mb_division else ""
        _date_processed = ""
        _grp_name = None
        tsv_items: list[int | str | None] = [
            self.log_id,
            self.date_received,
            _date_processed,
            self.category,
            self.type,
            self.employee_name,
            self.monetary_amount,
            self.time_off_amount,
            self.employee_pay_plan,
            self.employee_org,
            self.employee_supervisor_name,
            _grp_name,
            self.nominator_name,
            self.funding_org,
            self.mb_division,
            self.justification,
            self.value,
            self.extent,
        ]
        for idx, item in enumerate(tsv_items):
            if item is None:
                tsv_items[idx] = "-"
            else:
                tsv_items[idx] = str(item)

        tsv_string = "\t".join(tsv_items)

        with open(PathManager.tsv_output_path, "a", encoding="utf-8") as file:
            file.write(tsv_string + "\n")

        logger.info(f"'{PathManager.tsv_output_path.name}' updated with new data")

    def _rename_and_copy_file(self) -> None:
        """Renames and copies a file to an archive path."""
        if testing_mode or not isinstance(self.source_path, Path):
            return
        stem_items: list = [
            self.log_id,
            self.funding_org,
            self.employee_name,
            self.date_received,
        ]
        file_stem: str = " _ ".join(str(i) for i in stem_items)
        new_path: Path = self.source_path.with_stem(file_stem)
        renamed_path: Path = Path(self.source_path.rename(new_path))
        target_path: Path = PathManager.file_archive_dir / renamed_path.name
        try:
            shutil.copy2(renamed_path, target_path)
        except PermissionError:
            raise PermissionError(
                "Permission denied. The file is still open in another application. Please close the file and try again."
            )
        except Exception as e:
            logger.error(f"Error renaming and copying file: {e}")
        renamed_path.unlink()
        logger.info(f"File renamed and copied to '{PathManager.file_archive_dir.name}'")

    def _save_and_log(self) -> None:
        """Save data in different formats and log the category."""
        self._save_json()
        self._save_tsv()
        self._rename_and_copy_file()
        IDManager.update(self.category)

    def process_pdf_data(self) -> None:
        if self.source_path:
            pdf_data: dict[str, Optional[str]] = self.extract_pdf_data()
            self.populate_attributes(pdf_data)
        self._validate_and_transform()
        self._save_and_log()

        logger.info("PDF processing and data transformation complete.")
        logger.final(self._table())

    def process_manual_entry(self) -> None:
        """Loads and processes manual entry data."""
        print("\n", " Manual Entry Mode ".center(100, "-"), "\n")

        try:
            manual_entry_data: dict[str, str] = ManualEntry.load()
            self.category = "IND"
            self.log_id = IDManager.get(self.category)
            self.employee_name = Formatter(
                manual_entry_data.get("employee_name")
            ).name()
            self.employee_pay_plan = Formatter(
                manual_entry_data.get("employee_pay_plan")
            ).pay_plan()
            self.employee_org = Formatter(manual_entry_data.get("employee_org")).value()
            self.sas_monetary_amount = Formatter(
                manual_entry_data.get("sas_monetary_amount")
            ).numerical()
            self.sas_time_off_amount = Formatter(
                manual_entry_data.get("sas_time_off_amount")
            ).numerical()
            self.ots_monetary_amount = Formatter(
                manual_entry_data.get("ots_monetary_amount")
            ).numerical()
            self.ots_time_off_amount = Formatter(
                manual_entry_data.get("ots_time_off_amount")
            ).numerical()
            self.nominator_name = Formatter(
                manual_entry_data.get("nominator_name")
            ).name()
            self.nominator_org = Formatter(
                manual_entry_data.get("nominator_org")
            ).value()
            self.funding_string = Formatter(
                manual_entry_data.get("funding_string")
            ).value()
            self.certifier_name = Formatter(
                manual_entry_data.get("certifier_name")
            ).name()
            self.certifier_org = Formatter(
                manual_entry_data.get("certifier_org")
            ).value()
            self.employee_supervisor_name = Formatter(
                manual_entry_data.get("employee_supervisor_name")
            ).name()
            self.employee_supervisor_org = Formatter(
                manual_entry_data.get("employee_supervisor_org")
            ).name()
            self.approver_name = Formatter(
                manual_entry_data.get("approver_name")
            ).name()
            self.approver_org = Formatter(manual_entry_data.get("approver_org")).value()
            self.value = Formatter(manual_entry_data.get("value")).value()
            self.extent = Formatter(manual_entry_data.get("extent")).value()
            self.justification = Formatter(
                manual_entry_data.get("justification")
            ).justification()
            date_received = Formatter(manual_entry_data.get("date_received"))
            if date_received:
                self.date_received = date_received

            logger.info("Loaded manual entry data.")
            self.process_pdf_data()
            options = {1: "Reset Manual entry.", 2: "Pass."}
            while True:
                print("Make a selection.")
                [print(f"{k}: {v}") for k, v in options.items()]
                try:
                    selection: int = int(input(">>> ").strip())
                    if selection not in options:
                        raise ValueError
                    elif selection == 1:
                        ManualEntry.reset()
                    break
                except:
                    print("\nInvalid selection.\n")

        except Exception as e:
            logger.error(e)


if __name__ == "__main__":
    data = [
        {
            "file": "NNSA INDIVIDUAL Award Nomination Form - EOQ Q2 2025 - C. Santos.pdf",
            "error": "No monetary or time-off amounts found....",
        },
        {
            "file": "NNSA INDIVIDUAL Award Nomination Form - EOQ Q2 2025 - Timm.pdf",
            "error": "No monetary or time-off amounts found....",
        },
    ]
    table = tabulate(
        data,
        headers="keys",
        tablefmt="simple_outline",
    )
    print(table)

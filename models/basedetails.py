import warnings
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import NoneType
from typing import Optional

import fitz

from constants import CONSULTANT_MAP
from formatting.formatter import Formatter
from logger import Logger
from .employee import Employee
from .evaluator import Evaluator
from .empextractor import EmployeeExtractor
from utils import IDManager

logger = Logger()
formatter = Formatter()


@dataclass
class Base:
    source_path: Optional[Path | str] = None

    def __post_init__(self):
        self.log_id: Optional[str] = None
        self.funding_org: Optional[str] = None
        self.employee_data: dict[str, Employee] = {}
        self.total_monetary_amount: int = 0
        self.total_time_off_amount: int = 0
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

        self.pdf_data: dict[str, str | int | None] = {}

        self.evaluator = Evaluator()
        self.extractor: EmployeeExtractor = EmployeeExtractor()

        self.validate_source_path()
        if self.source_path:
            self.populate_base_fields()

    def validate_source_path(self) -> None:
        if self.source_path is None:
            return
        elif isinstance(self.source_path, str):
            self.source_path = Path(self.source_path.replace('"', "").strip())

        if not isinstance(self.source_path, Path):
            raise ValueError(
                f"Invalid source path type. Expected: [Path, str, None]. Received: {type(self.source_path)}"
            )
        if not self.source_path.is_file() or not self.source_path.exists():
            raise ValueError(
                f"Source path '{self.source_path}' is not a file or does not exist."
            )

    def extract_pdf_data(self) -> dict[str, Optional[str]]:
        warnings.filterwarnings("ignore", module="pymupdf")
        with fitz.open(self.source_path) as doc:
            if doc.page_count == 2:
                self.category = "IND"
            elif doc.page_count in [3, 4, 5]:
                self.category = "GRP"
            else:
                raise ValueError(
                    f"Invalid page count. Expected: [2, 3, 4, 5]  |  Received: {doc.page_count}"
                )
            self.log_id = IDManager.get(self.category)

            for page in doc:
                for field in page.widgets():
                    key = formatter.key(field.field_name)
                    if self.category == "GRP" and key not in self.evaluator.all_options:
                        key = f"{page.number}.{key}"
                    val = formatter.clean(field.field_value)
                    self.pdf_data[key] = val
        warnings.resetwarnings()

        if not self.pdf_data:
            raise ValueError("No data extracted from the PDF.")
        logger.info(f"Extracted {len(self.pdf_data)} items from PDF.")

    def get_first_match(self, *keys: str) -> Optional[str]:
        if not keys or not self.pdf_data:
            return None
        for key in keys:
            if key in self.pdf_data:
                return self.pdf_data[key]
        return None

    def set_value(self):
        value_fields: list[str] = []
        for val in self.evaluator.value_options:
            if str(self.pdf_data.get(val)).lower() == "on":
                value_fields.append(val)
        self.value = value_fields[0] if len(value_fields) == 1 else None

    def set_extent(self):
        extent_fields: list[str] = []
        for ext in self.evaluator.extent_options:
            if str(self.pdf_data.get(ext)).lower() == "on":
                extent_fields.append(ext)
        self.extent = extent_fields[0] if len(extent_fields) == 1 else None

    def _set_consultant(self) -> None:
        self.consultant = CONSULTANT_MAP.get(self.funding_org)
        if self.consultant is None:
            logger.warning(f"No consultant found for funding org '{self.funding_org}'")
        logger.info("Consultant set for funding organization.")

    def _evaluate_amounts(self):
        if self.value and self.extent:
            self.evaluator.value, self.evaluator.extent = self.value, self.extent

            for emp_data in self.employee_data.values():
                self.evaluator.employee_data.append(emp_data)

            self.evaluator.evaluate()

    def _sort_employee_data(self) -> dict[int, dict[str, str | int | None]]:
        if not self.employee_data:
            return self.employee_data

        names: list[str] = [str(name) for name in self.employee_data.keys()]
        names.sort()
        sorted_data: dict[int, Employee] = {}
        for idx, name in enumerate(names):
            sorted_data[idx + 1] = self.employee_data[name].as_dict()
        return sorted_data

    def __str__(self):
        return "\n".join(
            f"{k}: {v if not isinstance(v,NoneType) else '-'}"
            for k, v in self.as_dict().items()
        )

    def as_dict(self):
        total_monetary_amount = f"${self.total_monetary_amount}" if isinstance(self.total_monetary_amount,int) else self.total_monetary_amount
        total_time_off_amount = f"{self.total_time_off_amount} hours" if isinstance(self.total_time_off_amount,int) else self.total_time_off_amount
        source_path = (
            self.source_path.name
            if isinstance(self.source_path, Path)
            else self.source_path
        )
        justification = (
            f"{len(self.justification.split(' '))} words"
            if isinstance(self.justification, str)
            else self.justification
        )
        attributes: dict[str, str | int | None | dict[int, Employee]] = {
            "source_path": source_path,
            "log_id": self.log_id,
            "funding_org": self.funding_org,
            "funding_string": self.funding_string,
            "total_monetary_amount": total_monetary_amount,
            "total_time_off_amount": total_time_off_amount,
            "nominator_name": self.nominator_name,
            "nominator_org": self.nominator_org,
            "approver_name": self.approver_name,
            "approver_org": self.approver_org,
            "certifier_name": self.certifier_name,
            "certifier_org": self.certifier_org,
            "value": self.value,
            "extent": self.extent,
            "justification": justification,
            "category": self.category,
            "type": self.type,
            "date_received": self.date_received,
            "consultant": self.consultant,
            "employees": self._sort_employee_data(),
        }
        for k, v in attributes.items():
            if type(v) not in [dict, float, int, list, NoneType, str]:
                v = str(v)
                attributes[k] = v
        return attributes

    def populate_base_fields(self):
        self.extract_pdf_data()
        self.set_value()
        self.set_extent()

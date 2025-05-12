import re
from dataclasses import dataclass
from typing import Optional

from constants import ORGANIZATION_DIVISIONS
from formatting.formatter import Formatter
from logger import Logger

formatter = Formatter()
logger = Logger()


@dataclass
class OrgExtractor:
    input_string: Optional[str] = None

    def __post_init__(self):
        self.identified_org: Optional[str] = None
        self.identified_div: Optional[str] = None
        
        self._formatted_input: Optional[str] = None
        self._formatted_organization: Optional[str] = None
        self._formatted_division: Optional[str] = None
        
        self._field_office: Optional[str] = None

        if isinstance(self.input_string, str):
            self._formatted_input = formatter.standardized_org_div(self.input_string)
            self._extract_org_details()

    def extract(self) -> tuple[Optional[str], Optional[str]]:
        return self.identified_org, self.identified_div

    def __str__(self):
        return f"OrgExtractor(input_string={self.input_string}, identified_org={self.identified_org}, identified_div={self.identified_div})"

    def as_dict(self):
        return {
            "identified_org": self.identified_org,
            "identified_div": self.identified_div,
        }

    def _extract_org_details(self) -> None:
        for organization, divisions in ORGANIZATION_DIVISIONS.items():
            self._formatted_organization = formatter.standardized_org_div(organization)
            self._field_office = self._extract_field_office(organization)
            if self._org_similarity is True:
                self.identified_org = organization

            for division in list(reversed(divisions)):
                self._formatted_division = formatter.standardized_org_div(division)
                if self._division_similarity is True:
                    self.identified_org = organization
                    self.identified_div = division
                    break
            if self.identified_org and self.identified_div:
                return

    def _extract_field_office(self, organization: str) -> Optional[str]:
        parts = organization.split(" ")
        if len(parts) != 2:
            return None
        field_office = re.sub(r"[()]", "", parts[1].lower())
        return field_office

    @property
    def _org_similarity(self) -> bool:
        org_matches = (
            self._formatted_organization in self._formatted_input
            or self._formatted_input in self._formatted_organization
        )

        field_matches = False
        if isinstance(self._field_office, str):
            field_matches = self._field_office in self._formatted_input

        return org_matches or field_matches

    @property
    def _division_similarity(self) -> bool:
        return (
            self._formatted_division in self._formatted_input
            or self._formatted_input in self._formatted_division
        )

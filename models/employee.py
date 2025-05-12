import json
import re
from dataclasses import dataclass
from random import choice
from string import ascii_uppercase, digits
from typing import Optional
from constants import ORGANIZATION_DIVISIONS
from formatting.formatter import Formatter

from .orgextractor import OrgExtractor

formatter = Formatter()


@dataclass(order=True)
class Employee:
    name: Optional[str] = None
    org: Optional[str] = None
    pay_plan: Optional[str] = None
    supervisor_name: Optional[str] = None
    monetary_amount: Optional[int | str] = None
    time_off_amount: Optional[int | str] = None

    def __post_init__(self):
        self.identified_org: Optional[str] = None
        self.identified_div: Optional[str] = None
        self.random_employee: RandEmployee = RandEmployee()
        

    def __str__(self):
        return "\n".join(f"{key}: {value}" for key, value in self.as_dict().items())

    def as_dict(self) -> dict[str, int | str | None]:
        if type(self.monetary_amount) in [int,float]:
            self.fmtd_monetary_amount = f"${self.monetary_amount:,.2f}"
        if type(self.time_off_amount) in [int,float]:
            self.fmtd_time_off_amount = f"{self.time_off_amount} hours"
        return {
            "name": self.name,
            "org": self.org,
            "pay_plan": self.pay_plan,
            "supervisor_name": self.supervisor_name,
            "monetary_amount": self.fmtd_monetary_amount,
            "time_off_amount": self.fmtd_time_off_amount,
        }

    def _validate_pay_plan(self) -> None:
        if self.pay_plan is None:
            return
        if "es" in self.pay_plan.casefold():
            pay_plan = re.sub("es", "*ES*", self.pay_plan, flags=re.IGNORECASE)
            raise ValueError(
                f"'ES' pay plans are not permitted: '{self.pay_plan}' ({pay_plan})"
            )

    def validate(self) -> None:
        if isinstance(self.name, str):
            self.name = formatter.name(self.name)
        if isinstance(self.org, str):
            extractor = OrgExtractor(self.org)
            self.identified_org, self.identified_div = extractor.extract()
            self.org = (
                self.identified_div if self.identified_div else self.identified_org
            )
        if isinstance(self.pay_plan, str):
            self.pay_plan = formatter.pay_plan(self.pay_plan)
            self._validate_pay_plan()
        if isinstance(self.supervisor_name, str):
            self.supervisor_name = formatter.name(self.supervisor_name)
        self.monetary_amount = formatter.extract_int(self.monetary_amount)
        self.time_off_amount = formatter.extract_int(self.time_off_amount)

    def _is_valid_name(self):
        return self.name is not None

    def _is_valid_amount(self):
        return any(i is not None for i in [self.monetary_amount, self.time_off_amount])

    def is_valid(self) -> bool:
        self.validate()
        return all([self._is_valid_name(), self._is_valid_amount()])

    def randomize(self) -> None:
        rand_emp = RandEmployee()
        self.name = rand_emp.full_name
        self.org = rand_emp.org
        self.pay_plan = rand_emp.pay_plan
        self.supervisor_name = rand_emp.supervisor_name
        self.monetary_amount = rand_emp.monetary_amount
        self.time_off_amount = rand_emp.time_off_amount
        self.validate()


class RandEmployee:
    def __init__(self):
        self.name_data = self.load_data()
        monetary_options: list[int] = [i for i in range(0, 501, 25)]
        time_off_options: list[int] = [i for i in range(0, 41, 8)]
        self.first_name = choice(self.name_data["first_names"])
        self.last_name = choice(self.name_data["last_names"])
        self.full_name = f"{self.first_name} {self.last_name}"
        self.org = choice(list(ORGANIZATION_DIVISIONS))
        self.monetary_amount = choice(monetary_options)
        self.time_off_amount = choice(time_off_options)

    def __str__(self):
        return "\n".join(f"{key}: {value}" for key, value in self.as_dict().items())

    def as_dict(self) -> dict[str, int | str | None]:
        return {
            "name": self.full_name,
            "org": self.org,
            "pay_plan": self.pay_plan,
            "supervisor_name": self.supervisor_name,
            "monetary_amount": self.monetary_amount,
            "time_off_amount": self.time_off_amount,
        }

    @property
    def supervisor_name(self) -> str:
        first = choice(self.name_data["first_names"])
        last = choice(self.name_data["last_names"])
        return f"{first} {last}"
    
    @property
    def pay_plan(self) -> str:
        letters: str = "".join(choice(ascii_uppercase) for _ in range(2))
        numbers: str = "".join(choice(digits) for _ in range(2))
        return f"{letters}-{numbers}"

    def load_data(self) -> dict[str, list[str]]:
        path = r"data/random_name_data.json"
        with open(path, "r") as file:
            return json.load(file)


if __name__ == "__main__":
    from pprint import pprint
    rand_emp = RandEmployee()
    pprint(rand_emp.as_dict(),sort_dicts=False)

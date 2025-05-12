from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from utils import IDManager

@dataclass
class GrpEmployee:
    name: Optional[str] = None
    pay_plan: Optional[str] = None
    org: Optional[str] = None
    monetary_amount: Optional[str|int] = None
    time_off_amount: Optional[str|int] = None
    supervisor_name: Optional[str] = None



@dataclass
class GrpProcessor:
    source_path: Optional[Path | str] = None

    def __post_init__(self):
        self.log_id: Optional[str] = IDManager.get("GRP")
        self.funding_org: Optional[str] = None
        self.funding_string: Optional[str] = None
        self.nominator_name: Optional[str] = None
        self.nominator_org: Optional[str] = None
        self.certifier_name: Optional[str] = None
        self.certifier_org: Optional[str] = None
        self.approver_name: Optional[str] = None
        self.approver_org: Optional[str] = None
        self.administrator_name: Optional[str] = None
        self.reviewer_name: Optional[str] = None
        self.mb_division: Optional[str] = None
        self.justification: Optional[str] = None
        self.value: Optional[str] = None
        self.extent: Optional[str] = None
        self.category: Optional[str] = None
        self.type: Optional[str] = None
        self.date_received = datetime.now().strftime("%Y-%m-%d")
        self.consultant: Optional[str] = None

    def populate(self) -> None:
        pass
from dataclasses import dataclass
from pathlib import Path
from .groupdetails import Group
from .individualdetails import Individual

@dataclass(kw_only=True)
class PathGenerator:
    path: Path
    award: Individual | Group
    
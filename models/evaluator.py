from dataclasses import dataclass
from typing import Optional

from rich.traceback import install
from tabulate import tabulate

from .employee import Employee, RandEmployee

install(show_locals=True, width=150)


@dataclass
class Evaluator:
    value: Optional[str] = None
    extent: Optional[str] = None

    def __post_init__(self):
        self.value_options: tuple[str, str, str] = ("moderate", "high", "exceptional")
        self.extent_options: tuple[str, str, str] = ("limited", "extended", "general")

        self.monetary_amount: int = 0
        self.fmtd_monetary_amount = f"${self.monetary_amount:,.2f}"
        self.monetary_matrix: list[list[int]] = [
            [100, 200, 300],
            [400, 500, 600],
            [700, 800, 900],
        ]

        self.time_off_amount: int = 0
        self.fmtd_time_off_amount = f"{self.time_off_amount} hours"
        self.time_off_matrix: list[list[int]] = [
            [8, 16, 24],
            [32, 40, 48],
            [56, 64, 72],
        ]

        self.employee_data: list[Employee] = []

        self.fmtd_monetary_percentage: Optional[str] = None
        self.fmtd_time_off_percentage: Optional[str] = None
        self.fmtd_combined_percentage: Optional[str] = None

    @property
    def value_idx(self) -> Optional[int]:
        if self.value in self.value_options:
            return self.value_options.index(self.value)
        return None

    @property
    def extent_idx(self) -> Optional[int]:
        if self.extent in self.extent_options:
            return self.extent_options.index(self.extent)
        return None

    @property
    def monetary_limit(self) -> Optional[int]:
        if self.value_idx is not None and self.extent_idx is not None:
            return self.monetary_matrix[self.value_idx][self.extent_idx]
        return None

    @property
    def monetary_percentage(self) -> Optional[float]:
        if self.monetary_limit and self.monetary_amount:
            return (self.monetary_amount / self.monetary_limit) * 100
        return None

    @property
    def time_off_limit(self) -> Optional[int]:
        if self.value_idx is not None and self.extent_idx is not None:
            return self.time_off_matrix[self.value_idx][self.extent_idx]
        return None

    @property
    def time_off_percentage(self) -> Optional[float]:
        if self.time_off_limit and self.time_off_amount:
            return (self.time_off_amount / self.time_off_limit) * 100
        return None

    @property
    def combined_percentage(self) -> Optional[float]:
        if self.monetary_percentage and self.time_off_percentage:
            return self.monetary_percentage + self.time_off_percentage
        return None

    def add_employee(self, employee: Employee) -> None:
        try:
            self.employee_data.append(employee)
            self.monetary_amount += employee.monetary_amount
            self.time_off_amount += employee.time_off_amount
        except AttributeError as e:
            raise AttributeError(
                f"Employee object must have 'monetary_amount' and 'time_off_amount' attributes. {e}"
            )

    def evaluate(self) -> None:
        if self.combined_percentage is None:
            raise ValueError("Combined percentage cannot be None.")
        elif self.combined_percentage > 100:
            details_table = self.details_table()
            employee_table = self.employee_data_table()
            raise ValueError(
                f"Budget threshold exceeded: Combined allocation ({self.combined_percentage:.2f}%) is over the 100% limit.\n\n"
                f"Evaluation Details:\n{details_table}\n\n"
                f"Employee Allocations:\n{employee_table}\n\n"
            )
    
    def employee_data_table(self) -> str:
        """
        Returns a formatted table of the employee data.
        """
        headers = ["Name", "Monetary Amount", "Time Off Amount"]
        table_data = [
            [emp.name, emp.monetary_amount, emp.time_off_amount]
            for emp in self.employee_data
        ]        
        return tabulate(table_data, headers=headers, tablefmt="simple_outline")

    def details_table(self) -> str:
        _dict = self.as_dict()
        headers = ["Field", "Value"]
        table_data = [
            [key, value] for key, value in _dict.items()
        ]
        return tabulate(table_data, headers=headers, tablefmt="simple_outline")

    def __str__(self) -> str:
        return "\n".join(f"{key}: {value}" for key, value in self.as_dict().items())

    def as_dict(self) -> dict:
        if self.monetary_amount is not None:
            self.fmtd_monetary_amount = f"${self.monetary_amount:,.2f}"
        if self.time_off_amount is not None:
            self.fmtd_time_off_amount = f"{self.time_off_amount} hours"
        if self.monetary_percentage is not None:
            self.fmtd_monetary_percentage = f"{self.monetary_percentage:.2f}%"

        if self.time_off_percentage is not None:
            self.fmtd_time_off_percentage = f"{self.time_off_percentage:.2f}%"

        if self.combined_percentage is not None:
            self.fmtd_combined_percentage = f"{self.combined_percentage:.2f}%"
        return {
            "Value": self.value.capitalize() if self.value else None,
            "Extent": self.extent.capitalize() if self.extent else None,
            "Monetary Limit": self.fmtd_monetary_amount,
            "Time Off Limit": self.fmtd_time_off_amount,
            "Total Monetary Amount": self.fmtd_monetary_amount,
            "Total Time Off Amount": self.fmtd_time_off_amount,
            "Monetary Percentage": self.fmtd_monetary_percentage,
            "Time Off Percentage": self.fmtd_time_off_percentage,
            "Combined Percentage": self.fmtd_combined_percentage,
        }


def demo():
    print("\n\nDemo run of the Evaluator class\n\n")
    for _ in range(10):
        try:
            evaluator = Evaluator()
            evaluator.value = evaluator.value_options[-1]
            evaluator.extent = evaluator.extent_options[-1]
            for i in range(3):
                emp = Employee()
                emp.randomize()
                print(f"\nEmployee {i + 1}: {emp}\n")
                evaluator.add_employee(emp)
            evaluator.evaluate()
        except Exception as e:
            print(f"Error:\n{e}")
        finally:
            print("\n" + "=" * 50 + "\n")
    print("\n\nEvaluation complete.\n\n")


if __name__ == "__main__":
    demo()

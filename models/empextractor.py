from .employee import Employee


class EmployeeExtractor:
    employee_names: list[str] = []

    def __str__(self):
        return str(self.employee_names)

    def extract_employee(self, *values: str) -> Employee:
        employee = Employee(*values)
        if employee.name is not None and employee.name not in self.employee_names:
            self.employee_names.append(employee.name)
            return employee
        return Employee()

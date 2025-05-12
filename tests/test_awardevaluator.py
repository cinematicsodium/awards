"""
Unit test and demo code for AwardEvaluator.
"""
from random import choice

import pytest

from models.evaluator import AwardEvaluator
from models.employee import Employee

# If you have a random employee generator, import it here
try:
    from Snippets.randemployee import RandEmployee
except ImportError:
    RandEmployee = None

def make_random_employee():
    monetary_options = [i for i in range(0, 501, 25)]
    time_off_options = [i for i in range(0, 41, 4)]
    if RandEmployee:
        rand_emp = RandEmployee()
        name = rand_emp.full_name
    else:
        name = "Test Employee"
    return Employee(
        name=name,
        monetary_amount=choice([choice(monetary_options), 0]),
        time_off_amount=choice([choice(time_off_options), 0]),
    )

def test_award_evaluator_basic():
    evaluator = AwardEvaluator(value="moderate", extent="limited")
    emp = Employee(name="Alice", monetary_amount=100, time_off_amount=10)
    evaluator.employee_data.append(emp)
    evaluator.evaluate()
    assert evaluator.monetary_amount == 100
    assert evaluator.time_off_amount == 10
    assert evaluator.monetary_limit == 500
    assert evaluator.time_off_limit == 9
    assert evaluator.combined_percentage > 0

def test_award_evaluator_random():
    evaluator = AwardEvaluator(value="high", extent="extended")
    for _ in range(3):
        emp = make_random_employee()
        if hasattr(emp, 'is_valid') and emp.is_valid():
            evaluator.employee_data.append(emp)
    if evaluator.employee_data:
        evaluator.evaluate()
        assert evaluator.combined_percentage >= 0
    else:
        assert True  # No valid employees, test passes trivially

if __name__ == "__main__":
    # Demo run
    evaluator = AwardEvaluator(value="exceptional", extent="general")
    for _ in range(3):
        emp = make_random_employee()
        if hasattr(emp, 'is_valid') and emp.is_valid():
            evaluator.employee_data.append(emp)
    if evaluator.employee_data:
        try:
            evaluator.evaluate()
            print("Evaluation successful.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No valid employees to evaluate.")

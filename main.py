
from testing import sample_grp_employees
from constants import VALUES, EXTENTS
from validation import validate_grp_compensation
from random import choice

if __name__ == '__main__':
    for _ in range(5):
        employees = sample_grp_employees()
        value = choice(VALUES)
        extent = choice(EXTENTS)
        try:
            validate_grp_compensation(employees, value, extent)
        except ValueError as e:
            print(e)
            print('\n')
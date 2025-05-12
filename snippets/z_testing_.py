from datetime import datetime
from pathlib import Path

from rich.console import Console

from ind_processor import IndProcessor
from logger import Logger
from utils import clean_JSON_output

console = Console()
logger = Logger()


def get_last_modified(source_path: Path) -> str:
    last_modified_timestamp: float = source_path.stat().st_mtime
    last_modified: datetime = datetime.fromtimestamp(last_modified_timestamp).strftime(
        "%Y-%m-%d"
    )
    return last_modified


def pdf_testing():
    try:
        pdf_path = input("\nEnter pdf path: ").strip()
        processor = IndProcessor(pdf_path)
        processor.process_pdf_data()
    except Exception as e:
        logger.error(e)


def manual_entry_testing():
    processor = IndProcessor()
    processor.process_manual_entry()
    


def main():
    options: dict = {1: pdf_testing, 2: manual_entry_testing, 3: clean_JSON_output}

    while True:
        print("\nMake a selection")
        for k, v in options.items():
            print(f"{k}: {v.__name__}")

        try:
            user_input: str = input(">>> ").strip()
            key = int(user_input)
            if key not in options:
                raise ValueError
            func = options[key]
            func()
        except ValueError:
            print(
                "\nError:\n"
                f"Invalid input: {user_input}\n"
                f"Enter one of the following options: {list(options.keys())}"
            )
        except KeyboardInterrupt:
            print("\ngoodbye.\n")
            exit()

        except Exception as e:
            print(f"\nError:\n{e}")

"""
Test and demo code for AwardEvaluator.
"""
from random import choice

from models.evaluator import AwardEvaluator
from models.employee import Employee

# If you have a random employee generator, import it here
try:
    from Snippets.randemployee import RandEmployee
except ImportError:
    RandEmployee = None


def demo_award_evaluator():
    monetary_options = [i for i in range(0, 501, 25)]
    time_off_options = [i for i in range(0, 41, 4)]
    for _ in range(3):
        try:
            evaluator = AwardEvaluator()
            value = choice(evaluator.value_options)
            extent = choice(evaluator.extent_options)
            evaluator.value = value
            evaluator.extent = extent
            for _ in range(3):
                if RandEmployee:
                    rand_emp = RandEmployee()
                    name = rand_emp.full_name
                else:
                    name = f"Employee_{_}"
                employee = Employee(
                    name=name,
                    monetary_amount=choice([choice(monetary_options), 0]),
                    time_off_amount=choice([choice(time_off_options), 0]),
                )
                if hasattr(employee, 'is_valid') and employee.is_valid():
                    evaluator.employee_data.append(employee)
            evaluator.evaluate()
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    demo_award_evaluator()
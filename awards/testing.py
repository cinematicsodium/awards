from dataclasses import dataclass
from modules import EmpInfo, PDFInfo
from constants import PAY_PLANS
from fileFuncs import get_pdf_info
from random import choice, randint
from orgConfig import ORGS
from pprint import pprint  
@dataclass(frozen=True)


class TestFiles:
    ind: str = '/Users/Joey/Downloads/FormTemplates/SpecialActNominationForm_IND_max_01.pdf'
    grp14: str = '/Users/Joey/Downloads/FormTemplates/SpecialActNominationForm_GRP_max_14.pdf'
    grp21: str = '/Users/Joey/Downloads/FormTemplates/SpecialActNominationForm_GRP_max_21.pdf'
TEST_FILES = TestFiles()


FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Avery", "Peyton", "Quinn",
    "Cameron", "Drew", "Reese", "Skyler", "Rowan", "Emerson", "Finley", "Hayden", "Dakota", "Sawyer"
]


LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
    ]


HOURS_RANGE = list(range(4,40,4))
MONETARY_RANGE = list(range(50, 2000, 50))


def generate_name() -> str:
    return f'{choice(FIRST_NAMES)} {choice(LAST_NAMES)}'


def sample_ind_employee() -> EmpInfo:
    return EmpInfo(
        name=generate_name(),
        supervisor=generate_name(),
        org=choice(ORGS)[randint(0, 5)],
        pay_plan=choice(PAY_PLANS),
        monetary=choice(MONETARY_RANGE),
        hours=choice(HOURS_RANGE)
    )


def sample_grp_employees() -> list[EmpInfo]:
    return [
    EmpInfo(
        name=f'{choice(FIRST_NAMES)} {choice(LAST_NAMES)}',
        supervisor=f'{choice(FIRST_NAMES)} {choice(LAST_NAMES)}',
        org=choice(ORGS)[randint(0, 5)],
        pay_plan=choice(PAY_PLANS),
        monetary=choice(MONETARY_RANGE),
        hours=choice(HOURS_RANGE)
    )
    for _ in range(5)
]


def sample_ind_pdf() -> PDFInfo:
    file_name = TEST_FILES.ind
    fiscal_year = '2021'
    serial_number = 1
    pdf_info = get_pdf_info(file_name, fiscal_year, serial_number)
    return pdf_info


def sample_grp_pdf() -> PDFInfo:
    file_name = TEST_FILES.grp14
    fiscal_year = '2021'
    serial_number = 1
    pdf_info = get_pdf_info(file_name, fiscal_year, serial_number)
    return pdf_info


if __name__ == '__main__':
    print()
    print('Testing: IND'.center(100, '.'))
    pprint(sample_ind_pdf())
    print()
    print('Testing: GRP'.center(100, '.'))
    pprint(sample_grp_pdf())
    print()
    for i in range(5):
        print(generate_name())
from validation import validate_ind_compensation
from indFuncs import get_ind_award_details
from testing import sample_ind_pdf


def ind_award(file_path: str) -> None:
    ind_details = get_ind_award_details(file_path)
    validate_ind_compensation(ind_details)
    return ind_details

if __name__ == '__main__':
    test_ind_pdf = sample_ind_pdf()
    ind_details = get_ind_award_details(test_ind_pdf)
    validate_ind_compensation(ind_details)
    print(ind_details)
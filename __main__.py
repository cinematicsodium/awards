from modules import SerialNumbers, FYInfo, IndAwd, GrpAwd
from constants import *
from indFuncs import get_ind_award_details
from grpFuncs import get_grp_award_details
from fiscalYears import FISCAL_YEARS
from logger import SimpleLogger
from pathlib import Path
import fileFuncs


logger = SimpleLogger()


def finalize_processing(pdf_path: Path, fiscal_year: FYInfo, award_details: IndAwd | GrpAwd, testing: bool) -> None:
    fileFuncs.export_as_TSV(fiscal_year.award_details_TSV, award_details)
    fileFuncs.export_as_txt(fiscal_year.award_details_txt, award_details)
    if not testing:
        fileFuncs.insert_date_received(pdf_path, award_details.date_received)
        new_file_name = fileFuncs.generate_file_name(award_details)
        fileFuncs.archive_file(old_path=pdf_path, new_path=new_file_name, processed_dir=fiscal_year.archived_items_folder)
    logger.info(f'{pdf_path.name}: Processed successfully.')
    print(award_details)


def process_file(pdf_path: Path, fiscal_year: FYInfo, serial_numbers: SerialNumbers, testing: bool = False) -> IndAwd | GrpAwd:
    logger.info(f'{pdf_path.name}: Processing...')

    pdf_info = fileFuncs.extract_pdf_info(pdf_path, fiscal_year.year, serial_numbers)

    if pdf_info.category == 'IND':
        award_details = get_ind_award_details(pdf_info)
    elif pdf_info.category == 'GRP':
        award_details = get_grp_award_details(pdf_info)
    else:
        raise ValueError(f'Category not recognized for {pdf_info.file_name}')

    if not award_details:
        raise ValueError(f'{pdf_path.name}: No award details found for this file.')

    finalize_processing(pdf_path=pdf_path, fiscal_year=fiscal_year, award_details=award_details, testing=testing)

    return award_details

def initialize_processing(fiscal_year: FYInfo, testing=False) -> None:
    try:
        fy: str = fiscal_year.year
        print()
        print(f' Processing FY {fy} '.ljust(100, '.'))
        print()

        award_files_inbox = Path(fiscal_year.submissions_inbox)
        if testing:
            award_files_inbox = Path(TESTING_FOLDER)

        incoming_submission_files = list(award_files_inbox.glob('*.pdf'))
        if not incoming_submission_files:
            logger.info(f'No new submissions found for FY {fy}.\n')
            return
        incoming_submission_files.sort()

        serial_numbers: SerialNumbers = fileFuncs.load_serial_numbers(fiscal_year.serial_numbers_json)
        is_serial_numbers_updated = False

        rejected_files: list[str] = []

        file_count: int = 0
        for file in incoming_submission_files:

            print(f'file : {file_count + 1}\n')
            # if 'NA-IM' not in file.name:
            #     continue
            try:
                award_details: IndAwd|GrpAwd = process_file(pdf_path=file, fiscal_year=fiscal_year, serial_numbers=serial_numbers, testing=testing)
                if award_details:
                    if award_details.category == 'IND':
                        serial_numbers.IND += 1
                    elif award_details.category == 'GRP':
                        serial_numbers.GRP += 1
                    if not is_serial_numbers_updated:
                        is_serial_numbers_updated = True

            except Exception as e:
                rejected_files.append(file.name)
                logger.error(f'Unable to process {file.name}:\n\n{e}')
                if not testing:
                    fileFuncs.move_to_rejections(file_path=file, rejected_dir=fiscal_year.rejected_items_folder)
            
            print('.'*100+'\n')

        if rejected_files:
            rejected_count = len(rejected_files)
            formatted_list = '\n- '.join(file for file in rejected_files)
            logger.error(
                'Unable to process the following files:\n'
                f'- {formatted_list}'
                f'Rejected file count: {rejected_count}'
                )

        if testing:
            exit()
        elif is_serial_numbers_updated:
            fileFuncs.save_serial_numbers(fiscal_year.serial_numbers_json, serial_numbers)

    except Exception as e:
        logger.error(f'Error processing fiscal year {fy}:\n\n\t{e}')

def main() -> None:
    while True:
        print()
        print()
        try:
            testing: bool
            print(
                'Enter Selection\n'
                '0: STANDARD PROCESSING\n'
                '9: TESTING MODE'
            )
            selection: str = input('>>> ').strip()
            print()
            if selection == '0':
                testing = False
            elif selection == '9':
                testing = True
            else:
                raise ValueError(f'"{selection}" not in [0, 1]')

            for fiscal_year in FISCAL_YEARS:
                initialize_processing(fiscal_year=fiscal_year, testing=testing)

        except ValueError as e:
            print((f'\nInvalid selection: {e}\n'))


if __name__ == '__main__':
    main()

from modules import SerialNumbers, FiscalYear, IndAwd, GrpAwd
from indFuncs import get_ind_award_details
from grpFuncs import get_grp_award_details
from logger import SimpleLogger
from pathlib import Path
import fileFuncs


logger = SimpleLogger()


def finalize_processing(pdf_path: Path, fiscal_year: FiscalYear, award_details: IndAwd | GrpAwd) -> None:
    fileFuncs.export_as_TSV(fiscal_year.award_details_TSV, award_details)
    fileFuncs.export_as_txt(fiscal_year.award_details_txt, award_details)
    fileFuncs.insert_date_received(pdf_path, award_details.date_received)
    new_file_name = fileFuncs.generate_file_name(award_details)
    fileFuncs.archive_file(old_path=pdf_path, new_path=new_file_name, processed_dir=fiscal_year.archived_items_folder)
    logger.info(f'{pdf_path.name}: Processed successfully.')
    logger.info(award_details)


def process_file(file: Path, fiscal_year: FiscalYear, serial_numbers: SerialNumbers) -> IndAwd | GrpAwd:
    try:
        logger.info(f'{file.name}: Processing...')

        pdf_info = fileFuncs.extract_pdf_info(file, fiscal_year.year, serial_numbers)

        if pdf_info.category == 'IND':
            award_details = get_ind_award_details(pdf_info)
        elif pdf_info.category == 'GRP':
            award_details = get_grp_award_details(pdf_info)
        else:
            raise ValueError(f'Category not recognized for {pdf_info.file_name}')

        if not award_details:
            raise ValueError(f'{file.name}: No award details found for this file.')

        fileFuncs.finalize_processing(pdf_path=file, fiscal_year=fiscal_year, award_details=award_details)

        return award_details

    except FileNotFoundError as e:
        logger.error(f'File not found: {file.name} - {e}')
    except ValueError as e:
        logger.error(f'Unable to process {file.name}: {e}')


def process_fiscal_year(fiscal_year: FiscalYear) -> None:
    try:
        fy: str = fiscal_year.year
        print('\n' + f' Processing FY {fy} '.center(100, '.') + '\n')

        award_files_inbox = Path(fiscal_year.submissions_inbox)
        incoming_submission_files = list(award_files_inbox.glob('*.pdf'))
        if not incoming_submission_files:
            logger.info(f'No new submissions found for FY {fy}.\n')
            return

        serial_numbers: SerialNumbers = fileFuncs.load_serial_numbers(fiscal_year.serial_numbers_json)
        is_serial_numbers_updated = False

        for file in incoming_submission_files:
            try:
                award_details = process_file(file=file, fiscal_year=fiscal_year, serial_numbers=serial_numbers)
                finalize_processing(pdf_path=file, fiscal_year=fiscal_year, award_details=award_details)

                if award_details.category == 'IND':
                    serial_numbers.IND += 1
                elif award_details.category == 'GRP':
                    serial_numbers.GRP += 1
                is_serial_numbers_updated = True

            except Exception as e:
                logger.error(f'Unable to process {file.name}:\n\n{e}')
                fileFuncs.move_to_rejections(file_path=file, rejected_dir=fiscal_year.rejected_items_folder)

        if is_serial_numbers_updated:
            fileFuncs.save_serial_numbers(fiscal_year.serial_numbers_json, serial_numbers)

    except Exception as e:
        logger.error(f'Error processing fiscal year {fy}:\n\n{e}')

if __name__ == '__main__':
    pass
from processing import get_ind_award_details
from constants import PAGE_COUNTS
from fiscalyears import FISCAL_YEARS
from logger import SimpleLogger
from pathlib import Path
import fileFuncs

LINEBREAK = '\n' + '.'*100 + '\n'*2

for fiscal_year in FISCAL_YEARS:
    fy = fiscal_year.year
    print('\n' + f' FY {fy} '.center(100, '.') + '\n')

    incoming_submissions_dir        = Path(fiscal_year.new_submissions)
    processed_submissions_directory = Path(fiscal_year.processed_folder)
    serial_numbers_file             = Path(fiscal_year.serial_numbers)
    tsv_file                        = Path(fiscal_year.TSV_file)

    incoming_submission_files = list(incoming_submissions_dir.glob('*.pdf'))
    if not incoming_submission_files:
        print(f'No new submissions found for {fy}.\n')
        continue

    serial_numbers = fileFuncs.get_serial_numbers(serial_numbers_file)

    for file in incoming_submission_files:
        try:
            SimpleLogger().info(f'{file.name}: Processing...')

            award_details = None
            pdf_info = fileFuncs.get_pdf_info(file, fy, serial_numbers.IND)
            if pdf_info.category == 'IND':
                award_details = get_ind_award_details(pdf_info)
                serial_numbers.IND += 1
            elif pdf_info.category == 'GRP':
                pass
            else:
                SimpleLogger().error(f'Category not recognized for {pdf_info.file_name}')
                continue

            if award_details:
                new_file_name = fileFuncs.generate_new_file_name(ind_award=award_details)
                
                fileFuncs.export_as_TSV(tsv_file, award_details)
                fileFuncs.insert_date_received(award_details, award_details.date_received)
                fileFuncs.archive_file(
                    old_path=file, 
                    new_path=new_file_name, 
                    processed_dir=processed_submissions_directory
                    )
                
                print(award_details)
            else:
                SimpleLogger().error(f'{pdf_info.file_name}: No award details found for this file.')
        except Exception as e:
            err_msg = f'Error processing {file.name}:\n\n{e}'
            SimpleLogger().error(LINEBREAK + err_msg)
            continue

    fileFuncs.save_serial_numbers(serial_numbers_file, serial_numbers)
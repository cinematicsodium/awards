from typing import Dict, Generator, List, Optional, Union
from datetime import datetime, time, timedelta
from pprint import pprint
from pathlib import Path
import shutil
import fitz #type: ignore
import json
import os



_testing_: bool = False
_example_: bool = False
_print_data_: bool = True
_write_xls_rows_: bool = True
_insert_date_: bool = True
_rename_move_file_: bool = True
_update_serial_numbers_: bool = True

if _example_:
    _insert_date_ = False
    _rename_move_file_ = False
    _update_serial_numbers_ = False

received_date_is_tomorrow: bool = False
current_time = datetime.now().time()
cutoff_time = time(14,45)
if current_time > cutoff_time:
    received_date_is_tomorrow = True






def format_and_save(fileName: str, award_data: dict) -> str:
    formatted_data: dict = award_data.copy()
    k_len = max([len(k) for k in formatted_data.keys()])
    formatted_data["Justification"] = (
        str(len(formatted_data["Justification"].split())) + " words"
    )
    if formatted_data["Category"] == "IND":
        formatted_data["Monetary"] = "$" + str(formatted_data["Monetary"])
        formatted_data["Hours"] = str(formatted_data["Hours"]) + " hours"
        formatted_data["Nominee"] = (
            f"{formatted_data['Nominee']}    {formatted_data['Monetary']}    {formatted_data['Hours']}"
        )
        del formatted_data["Monetary"]
        del formatted_data["Hours"]
    elif formatted_data["Category"] == "GRP":
        nominees = formatted_data["Nominees"]
        formatted_data["Nominees"] = format_grp_nominees(nominees)
    res: str = (
        fileName
        + '\n\n'
        + "\n".join(f"{(k + ':').ljust(k_len + 2)} {v}" for k, v in formatted_data.items())
        + '\n'
        + "." * 50
        + '\n\n'
    )
    with open(r"process_award_data\awards_output.txt", "a") as f:
        f.write(res)
    return res

def createNewFileName(award_data: dict) -> str:
    id: str = award_data["Award ID"]
    org: str = award_data["Funding Org"]
    nominee: str = (
        award_data["Nominee"]
        if award_data.get("Nominee")
        else str(len(award_data["Nominees"])) + " nominees"
    )
    date: str = award_data["Date Received"]
    return " - ".join(
        [
            id,
            org,
            nominee,
            date,
        ]
    )

def create_new_file_path(original_path: Path, new_file_name: str) -> Path:
    return original_path.parent / f"{new_file_name}.pdf"

def validate_file_name(file_name: str) -> None:
    if not file_name.strip():
        raise ValueError("New file name cannot be empty.")
    if "/" in file_name or "\\" in file_name:
        raise ValueError("New file name cannot contain path separators.")

def renameAwardFile(file_path: str, new_file_name: str) -> Optional[Path]:
    try:
        validate_file_name(new_file_name)
        
        original_path = Path(file_path)
        new_path = create_new_file_path(original_path, new_file_name)
        
        original_path.rename(new_path)
        return new_path
    
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except PermissionError:
        print(f"Permission denied when renaming file: {file_path}")
    except ValueError as ve:
        print(f"Invalid file name: {ve}")
    except Exception as e:
        print(f"Error occurred while renaming file: {e}")
    return None

def determine_grp_configuration(page_count: int) -> list[list]:
    base_config = [
        ("employee name_2", "award amount", "time off hours"),
        ("employee name_3", "award amount_2", "time off hours_2"),
        ("employee name_4", "award amount_3", "time off hours_3"),
        ("employee name_5", "award amount_4", "time off hours_4"),
        ("employee name_6", "award amount_5", "time off hours_5"),
        ("employee name_7", "award amount_6", "time off hours_6"),
        ("employee name_8", "award amount_7", "time off hours_7"),
    ]

    additional_config_14 = [
        ("employee name_9", "award amount_8", "time off hours_8"),
        ("employee name_10", "award amount_9", "time off hours_9"),
        ("employee name_11", "award amount_10", "time off hours_10"),
        ("employee name_12", "award amount_11", "time off hours_11"),
        ("employee name_13", "award amount_12", "time off hours_12"),
        ("employee name_14", "award amount_13", "time off hours_13"),
    ]

    additional_config_21 = [
        ("employee name_1", "award amount", "time off hours"),
        ("employee name_15", "award amount_14", "time off hours_14"),
        ("employee name_16", "award amount_15", "time off hours_15"),
        ("employee name_17", "award amount_16", "time off hours_16"),
    ]

    if page_count == 3:
        return base_config
    elif page_count == 4:
        return base_config + additional_config_14
    elif page_count == 5:
        return additional_config_21 + base_config + additional_config_14
    return []

def get_grp_nominees_names_and_award_amounts(
    grp_nominees_fields: list[list], mid_page_fields: dict
) -> list[dict]:
    nominees_detected: list = []
    nominees_processed: list = []
    no_award_amounts_found: list = []

    for nominee_fields in grp_nominees_fields:
        nominee_name_field: str = nominee_fields[0]
        monetary_field: str = nominee_fields[1]
        hours_field: str = nominee_fields[2]
        current_nominee: dict = {"Name": None, "Monetary": 0, "Hours": 0}

        for field_name, field_text in mid_page_fields.items():
            if "left blank" in field_text.lower():
                continue
            field_text = xname(field_text)
            if "employee name" in field_name and (field_name,field_text) not in nominees_detected:
                nominees_detected.append((field_name,field_text))
            current_nominee["Name"] = (
                xname(field_text)
                if current_nominee["Name"] is None and field_name == nominee_name_field
                else current_nominee["Name"]
            )
            current_nominee["Monetary"] = (
                xnumerical(field_text)
                if field_name == monetary_field
                else current_nominee["Monetary"]
            )
            current_nominee["Hours"] = (
                xnumerical(field_text)
                if field_name == hours_field
                else current_nominee["Hours"]
            )

        if current_nominee["Name"] is not None:
            if current_nominee["Monetary"] == 0 and current_nominee["Hours"] == 0:
                if len(grp_nominees_fields) == 21 and nominee_fields in (
                    grp_nominees_fields[13],
                    grp_nominees_fields[14],
                ):
                    continue
                no_award_amounts_found.append(
                    ", ".join(f"{k}: {v}" for k, v in current_nominee.items())
                )
            nominees_processed.append(current_nominee)
    if len(nominees_detected) == 0:
        raise ValueError("No nominees detected.")
    elif len(nominees_processed) == 0:
        raise ValueError("Unable to process nominees.")
    elif len(nominees_detected) > len(nominees_processed):
        join_detected = "\n\t".join(str(i) for i in nominees_detected)
        join_processed = "\n\t".join(str(i) for i in nominees_processed)
        det_pro_err_0 = "Error:"
        det_pro_err_1 = (
            "Number of nominees detected does not match number of nominees processed\n"
        )
        det_pro_err_2 = f"Detected: {len(nominees_detected)}\n\t{join_detected}\n"
        det_pro_err_3 = f"Processed: {len(nominees_processed)}\n\t{join_processed}\n"
        det_pro_err_msg = (
            "\n".join(
                [
                    det_pro_err_0,
                    det_pro_err_1,
                    det_pro_err_2,
                    det_pro_err_3,
                ]
            )
            + "\n"
        )
        raise Exception(det_pro_err_msg)
    elif no_award_amounts_found:
        join_no_award = "\n\t".join(str(i) for i in no_award_amounts_found)
        raise Exception(f"Error: No award amounts found.\n\t{join_no_award}\n")
    return nominees_processed

def format_grp_nominees(nominees: list[dict]) -> str:
    max_name_len = max([len(nominee["Name"]) for nominee in nominees]) + 5
    max_monetary_len = max([len(str(nominee["Monetary"])) for nominee in nominees]) + 5
    return "\n    " + "\n    ".join(
        f"{(nominee['Name']+':').ljust(max_name_len)}${str(nominee['Monetary']).ljust(max_monetary_len)}{nominee['Hours']} hours"
        for nominee in nominees
    )

def process_grp_award_data(pdf_fields: dict, grp_sn: int) -> dict:
    last_page_fields: dict = pdf_fields["last_page"]
    mid_pages_fields = pdf_fields["mid_pages"]
    grp_award_data: dict = {
        "Award ID": "24-GRP-" + str(grp_sn).zfill(3),
    }
    shared_ind_grp_data: dict = get_shared_ind_grp_data(pdf_fields)
    grp_award_data.update(shared_ind_grp_data)
    grp_award_data["Category"] = "GRP"
    group_configuration = determine_grp_configuration(pdf_fields["page_count"])
    nominees = get_grp_nominees_names_and_award_amounts(group_configuration, mid_pages_fields)
    value_and_extent: dict = get_value_and_extent(last_page_fields)
    if value_and_extent:
        validate_award_amounts(nominees, value_and_extent, is_group=True)
        grp_award_data["Value"] = value_and_extent["Value"]["Text"]
        grp_award_data["Extent"] = value_and_extent["Extent"]["Text"]
    grp_award_data["Nominees"] = nominees
    grp_award_data["Date Received"] = determine_date_received(pdf_fields)
    return grp_award_data

def get_ind_name_amounts(first_page_fields: dict) -> dict:
    ind_name_amounts: dict = {
        "Name": None,
        "Monetary": 0,
        "Hours": 0,
    }
    for field_name, field_text in first_page_fields.items():
        if ind_name_amounts["Name"] is None and field_name == "employee name":
            ind_name_amounts["Name"] = xname(field_text)

        elif (
            ind_name_amounts["Monetary"] == 0
            and field_name in ["amount", "undefined"]
            or "the spot" in field_name
        ):
            ind_name_amounts["Monetary"] = xnumerical(field_text)

        elif ind_name_amounts["Hours"] == 0 and "hours" in field_name:
            ind_name_amounts["Hours"] = xnumerical(field_text)
    ind_name_amounts_str = "\t".join(f"{k}: {v}" for k, v in ind_name_amounts.items())
    if ind_name_amounts["Monetary"] == 0 == ind_name_amounts["Hours"]:
        raise Exception(f"No award amount found.\n{ind_name_amounts_str}\n")
    elif ind_name_amounts["Name"] is None:
        raise Exception("Unable to determine IND award nominee")
    return ind_name_amounts


def process_ind_award_data(pdf_fields: dict, ind_sn: int) -> dict:
    first_page_fields: dict = pdf_fields["first_page"]
    last_page_fields: dict = pdf_fields["last_page"]
    ind_award_data: dict = {
        "Award ID": "24-IND-" + str(ind_sn).zfill(3),
    }
    # if str(pdf_fields["file_name"]).startswith("24-"):
    #     ind_award_data["Award ID"] = pdf_fields["file_name"].split(" ")[0]
    shared_ind_grp_data: dict = get_shared_ind_grp_data(pdf_fields)
    ind_award_data.update(shared_ind_grp_data)
    ind_award_data["Category"] = "IND"
    nominee_name_award_amounts: dict = get_ind_name_amounts(first_page_fields)
    value_and_extent: dict = get_value_and_extent(last_page_fields)
    if value_and_extent:
        validate_award_amounts(nominee_name_award_amounts, value_and_extent, is_individual=True)
        ind_award_data["Value"] = value_and_extent["Value"]["Text"]
        ind_award_data["Extent"] = value_and_extent["Extent"]["Text"]
    ind_award_data["Nominee"] = nominee_name_award_amounts["Name"]
    ind_award_data["Monetary"] = nominee_name_award_amounts["Monetary"]
    ind_award_data["Hours"] = nominee_name_award_amounts["Hours"]
    ind_award_data["Date Received"] = determine_date_received(pdf_fields)
    if ind_award_data["Nominator"] == ind_award_data["Nominee"]:
        award_error: str = "\n".join(f"{k}: {v}" for k,v in ind_award_data.items())
        raise ValueError(f"Error: Nominator == Nominee\n\n{award_error}")
    return ind_award_data


def getSerialNums() -> dict:
    with open(AWARD_SER_NUMS, "r") as f:
        jsonSerNums = json.load(f)
        serialNums: dict[str,int] = {
            "IND": jsonSerNums["IND"],
            "GRP": jsonSerNums["GRP"],
        }
        return serialNums


def updateSerialNums(serialNums: dict) -> None:
    with open(AWARD_SER_NUMS, "w") as f:
        json.dump(serialNums, f, indent=4)


def move_file(filePath: str) -> None:
    shutil.move(filePath, FY24_FOLDER)


def processFiles(file_paths) -> None:
    serialNums: dict = getSerialNums()
    indID: int = serialNums["IND"]
    grpID: int = serialNums["GRP"]
    notProcessed: list[str] = []
    for file_path in file_paths:
        fileName: str = os.path.basename(file_path)
        if fileName.startswith("#"):
            continue
        try:
            pdfFields: dict = get_pdf_fields(file_path)
            awardCategory: str = pdfFields["category"]
            awardData: dict = {}
            formattedData: str = ""
            if awardCategory == "GRP":
                awardData = process_grp_award_data(pdfFields, grpID)
            else:
                awardData = process_ind_award_data(pdfFields, indID)
            if _write_xls_rows_:
                export_as_TSV(awardData)
            if _print_data_:
                formattedData = format_and_save(fileName,awardData)
                print(formattedData)
            if not _testing_:
                if _insert_date_:
                    insertDateReceived(str(file_path), awardData)
                newFileName: str = createNewFileName(awardData)
                if _rename_move_file_:
                    newFilePath = renameAwardFile(file_path, newFileName)
                    move_file(newFilePath)
            if awardCategory == "GRP" and str(grpID).zfill(3) in newFileName.split()[0]:
                grpID += 1
            elif awardCategory == "IND" and str(indID).zfill(3) in newFileName.split()[0]:
                indID += 1
        except Exception as e:
            hash_block: str = "#####\n"*5
            error_message = (
f"""
{hash_block}
{fileName}
{e}
{'.' * 50}
"""
)
            print(error_message)
            with open(r'process_award_data\awards_output.txt','a') as f:
                f.write(error_message+"\n")
            notProcessed.append(fileName)
    if _update_serial_numbers_ and not _testing_:
        updateSerialNums({"IND": indID, "GRP": grpID})
    if len(notProcessed) > 0:
        print(f"Not Processed ({len(notProcessed)}):")
        print("\n".join(notProcessed))


if __name__ == "__main__":
    print()
    print(" START ".center(100, "."))
    print()
    try:
        folderPath: str = PROCESSING_FOLDER if not _testing_ else TEST_FOLDER
        file_paths: Generator = Path(folderPath).rglob("*pdf")
        processFiles(file_paths=file_paths)
    except Exception as e:
        print(e)
    print()
    print(" END ".center(100, "."))
    if received_date_is_tomorrow:
        print('RECEIVED DATE == TOMORROW\n'*5)

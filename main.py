from pathlib import Path

from tabulate import tabulate

from .constants import testing_mode
from .ind_processor import IndProcessor
from .logger import Logger
from .utils import update_serial_numbers

logger = Logger()


def main():
    if not testing_mode:
        update_serial_numbers()
    try:
        processed_list: list[str] = []
        failed_list: list[dict[str, str]] = []

        folder: Path = Path(
            r"C:\Users\joseph.strong\OneDrive - US Department of Energy\Python\awards\_submissions"
        )

        for pdf_path in folder.iterdir():
            if pdf_path.is_file() and pdf_path.suffix == ".pdf":
                if "GRP" in pdf_path.name or "NA-90" in pdf_path.name:
                    continue
                try:
                    processor = IndProcessor(pdf_path)
                    processor.process_pdf_data()
                    processed_list.append(pdf_path.name)

                except Exception as e:
                    logger.error(e)
                    e = " ".join(str(e).split(" ")[:12]) + "..."
                    failed_list.append({"file": pdf_path.name, "error": e})

        logger.info(f"\n\nProcessed Files Count: {len(processed_list)}")
        if processed_list:
            processed_table = tabulate(
                {"processed": processed_list}, tablefmt="simple_outline", headers="keys"
            )
            logger.info(f"\n{processed_table}")

        logger.info(f"\n\nProcess Failure Count: {len(failed_list)}")
        if failed_list:
            failed_table = tabulate(
                failed_list, tablefmt="simple_outline", headers="keys"
            )
            logger.info(f"\n{failed_table}")
        logger.dash()
    except Exception as e:
        logger.error(f"\n{pdf_path.stem}\n{e}")
    except KeyboardInterrupt:
        print("\nGoodbye!\n")


if __name__ == "__main__":
    main()

from dataclasses import dataclass
from pathlib import Path

import fitz

from formatting.formatter import Formatter

formatter = Formatter()
from rich.traceback import install
install(show_locals=True, width=150)


@dataclass
class File:
    path: Path

    def __post_init__(self):
        try:
            self.path = Path(self.path)
        except TypeError:
            raise TypeError(f"Path {self.path} is not a valid path.")
        if not self.path.exists():
            raise FileNotFoundError(f"Path {self.path} does not exist.")
        if not self.path.is_file():
            raise ValueError(f"Path {self.path} is not a file.")
        self.new_path = self.generate_path()

    def is_ind_file(self):
        with fitz.open(self.path) as doc:
            return doc.page_count == 2

    def reset(self):
        with fitz.open(self.path) as doc:
            for page in doc:
                for field in page.widgets():
                    try:
                        widget = page.load_widget(field.xref)
                        widget.field_value = ""
                        widget.update()
                    except:
                        pass
            doc.save(self.new_path)

    def generate_path(self) -> Path:
        counter = 1
        stem = f"IND_{counter}"
        new_path = self.path.with_stem(stem)
        while new_path.exists():
            counter += 1
            stem = f"IND_{counter}"
            new_path = self.path.with_stem(stem)
        return new_path


def main():
    print("\n\nDeleting and resetting files...\n\n")
    folder: Path = Path("/Users/Joey/Downloads/SAS Forms")
    for file_path in folder.iterdir():
        if file_path.suffix != ".pdf":
            continue
        file = File(file_path)
        if not file.is_ind_file():
            print(f"Deleting {file.path}")
            file_path.unlink()
        else:
            print(f"Resetting {file.path}")
            file.reset()
            print(f"Renamed to {file.new_path.name}")
    print("\n\nDone.\n\n")


if __name__ == "__main__":
    main()

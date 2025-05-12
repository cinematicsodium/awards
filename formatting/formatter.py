import re
from typing import Optional

from rich.traceback import install

TITLES: list[str] = [
    "dr.",
    "mr.",
    "mrs.",
    "miss.",
    "ms.",
    "prof.",
    "ph.d",
]
title_count: int = len(TITLES)
for title_idx in range(title_count):
    TITLES.append(TITLES[title_idx].replace(".", ""))

NAME_PARTICLES = [
    "mc",
    "st",
    "st.",
    "de",
    "da",
    "di",
    "du",
    "la",
    "le",
    "el",
    "lo",
    "am",
    "op",
    "te",
    "zu",
    "zu",
    "im",
    "af",
    "av",
    "al",
    "ov",
    "ev",
]


class NameFormatter:

    @staticmethod
    def _is_valid(part: str) -> bool:
        def is_title(part: str) -> bool:
            pattern = r"\b[a-zA-Z]{2,4}\.(?:[a-zA-Z])?\.?(?:\s|$)"
            return re.match(pattern, part) is not None

        def is_enclosed(part: str) -> bool:
            pattern = re.compile(r"(['\"])([a-zA-Z]{1,12})\1|(\()([a-zA-Z]{1,32})(\))")
            return pattern.match(part) is not None

        def is_abbreviation(part: str) -> bool:
            pattern = re.compile(r"\b[A-Za-z]\.")
            try:
                return len(part) == 2 and pattern.match(part) is not None
            except:
                return False

        return any(
            [
                part.lower() in NAME_PARTICLES,
                all(
                    [
                        not is_title(part),
                        not is_enclosed(part),
                        not is_abbreviation(part),
                        not len(part) == 1,
                    ]
                ),
            ]
        )

    @staticmethod
    def _name_parts(name_string: str) -> list[str]:
        parts = name_string.split(" ")
        filtered_parts = []
        for part in parts:
            if NameFormatter._is_valid(part):
                filtered_parts.append(part)
        return filtered_parts

    @staticmethod
    def format_last_first(name_string: str) -> Optional[str]:
        if not name_string:
            return

        filtered_parts = NameFormatter._name_parts(name_string)
        if len(filtered_parts) not in range(2, 6):
            return name_string

        elif len(filtered_parts) == 5:
            first_name, last_name, preposition = filtered_parts[:3]
            if preposition != "for":
                return name_string

        elif len(filtered_parts) == 4:
            first_name, preposition, article, noun = filtered_parts
            if (
                preposition.lower() in NAME_PARTICLES
                and article.lower() in NAME_PARTICLES
            ):
                last_name = f"{preposition} {article} {noun}"
            else:
                return name_string

        elif len(filtered_parts) == 3:
            first_name, preposition, article = filtered_parts
            if preposition.lower() in NAME_PARTICLES:
                last_name = f"{preposition} {article}"
            else:
                last_name, first_name = filtered_parts[:2]
                if not last_name.endswith(","):
                    return name_string

        elif len(filtered_parts) == 2:
            if "," in filtered_parts[0]:
                last_name, first_name = filtered_parts[0], filtered_parts[1]
            else:
                first_name, last_name = filtered_parts

        last_name = last_name if last_name.endswith(",") else f"{last_name},"

        full_name: str = f"{last_name} {first_name}"

        capitalized_count: int = len(re.findall(r"[A-Z]", full_name))
        if 2 <= capitalized_count <= 5:
            return full_name
        return full_name.title()


class Formatter:

    def clean(self, text: str) -> Optional[str]:
        if not isinstance(text,str):
            return text
        text = text.encode("ascii", errors="ignore").decode("utf-8")

        regex_map: dict[str, str] = {
            r"\r": "\n",
            r"\n{2,}": "\n",
            r"\t": " ",
            r" {2,}": " ",
        }

        for pattern, replacement in regex_map.items():
            text = re.sub(pattern, replacement, text)
        return text.strip()

    def key(self, text: str) -> Optional[str]:
        if not isinstance(text,str):
            return text
        text = self.clean(text)
        return self.clean(text).lower().replace(" ", "_")

    def name(self, text: str) -> Optional[str]:
        if not isinstance(text,str):
            return text
        text = self.clean(text)
        return NameFormatter.format_last_first(text)

    def _is_list_item(self, line: str) -> bool:
        return re.match(r"^[a-zA-Z0-9]{1,3}\.", line) is not None

    def _format_lines(self, text: str) -> list[str]:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for idx, line in enumerate(lines):
            if line[0].isalnum() and not Formatter._is_list_item(line):
                lines[idx] = f"> {line}"
            else:
                lines[idx] = f"    {line}"
        return lines

    def justification(self, text: str) -> Optional[str]:
        if not isinstance(text,str):
            return text
        text = self.clean(text)
        text = text.replace('"', "'")
        lines = self._format_lines(text)
        text = "\n".join(lines)
        return f'"{text}"'

    def extract_int(self, text: str) -> Optional[int]:
        if not isinstance(text,str):
            return text
        text = self.clean(text)
        pattern = r"\s*([\d,]*\d(?:\.\d+)?)"
        match = re.search(pattern, text)
        if match is None:
            raise ValueError(f"Unable to extract numerical value from '{text}'")
        number = float(match.group(1).replace(",", ""))
        return number

    def standardized_org_div(self, text: str) -> Optional[str]:
        if not isinstance(text,str):
            return text
        text = self.clean(text)
        return text.replace("-", "").replace(" ", "").lower().strip()

    def _format_part(self, part: str) -> str:
        trimmed_part = re.sub(r"^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$", "", part)
        formatted_part = re.sub(
            r"[^a-zA-Z0-9]+",
            lambda match: (
                "-" if match.start() != 0 and match.end() != len(trimmed_part) else ""
            ),
            trimmed_part,
        ).upper()
        final_output = re.sub(r"-+", "-", formatted_part)
        return final_output

    def _format_parts(self, text: str) -> list[str]:
        parts = [part.strip() for part in text.split(" ")]
        formatted_parts = []
        for part in parts:
            part = self._format_part(part)
            formatted_parts.append(part) if part else None
        return formatted_parts

    def pay_plan(self, text: str) -> Optional[str]:
        if not isinstance(text,str):
            return text
        text = self.clean(text)
        formatted_parts = self._format_parts(text)
        return "_".join(formatted_parts) if formatted_parts else None

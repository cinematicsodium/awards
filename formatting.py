from icecream import ic
import unicodedata
import re

class Formatting:
    TITLES = {'Dr.', 'Mr.', 'Mrs.', 'Miss.', 'Ms.', 'Prof.'}

    @staticmethod
    def justification(field_text: str) -> str:
        if not field_text:
            return ''

        justif_str = unicodedata.normalize('NFKD', field_text).encode('ascii', 'ignore').decode('ascii')
        justif_str = justif_str.replace('"', "'").replace('  ', ' ')
        return f'"{justif_str}"'

    @staticmethod
    def name(field_text: str) -> str:
        if not field_text:
            return ''

        name_parts = [
            name.strip() for name in field_text.split()
            if name and name not in Formatting.TITLES and not (
                (name.startswith('"') and name.endswith('"')) or
                (name.startswith('(') and name.endswith(')')) or
                (len(name) == 3 and name.endswith('.'))
            )
        ]

        if len(name_parts) == 2:
            if ',' in name_parts[0]:  # Last, First
                return ' '.join(name_parts).title()
            elif '.' not in name_parts[0] and '.' not in name_parts[1]:  # First Last
                return f'{name_parts[1]}, {name_parts[0]}'.title()

        elif len(name_parts) == 3:
            if '.' in name_parts[0]:  # F_Initial Middle Last
                return f'{name_parts[2]}, {name_parts[0]} {name_parts[1]}'.title()
            elif '.' in name_parts[1]:  # First M_Initial Last
                return f'{name_parts[2]}, {name_parts[0]} {name_parts[1]}'.title()

        return ' '.join(name_parts).title()

    @staticmethod
    def numerical(field_text: str) -> float:
        if not field_text:
            return 0.0
        digits = ''.join(c for c in field_text if c.isdigit() or c == '.')
        try:
            return float(digits) if digits else 0.0
        except ValueError:
            return 0.0

if __name__ == '__main__':
    pass

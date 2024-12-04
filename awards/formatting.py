from icecream import ic
import unicodedata
import re

class Formatting:
    TITLES = ['Dr.', 'Mr.', 'Mrs.', 'Miss.', 'Ms.', 'Prof.']

    @staticmethod
    def justification(field_text: str) -> str:
        if not field_text:
            return ''

        justif_str = field_text.strip()
        justif_str = unicodedata.normalize('NFKD', justif_str).encode('ascii', 'ignore').decode('ascii')
        justif_str = justif_str.replace('"', "'")
        justif_str = re.sub(r'\s+', ' ', justif_str)
        return f'"{justif_str}"'

    @staticmethod
    def name(field_text: str) -> str:
        if not field_text:
            return ''

        formatted_name: str = ''

        name_parts = field_text.split()
        name_parts = [
            name.strip() for name in name_parts
            if name and all([
                name not in Formatting.TITLES,
                not (name.startswith('"') and name.endswith('"')),
                not (name.startswith('(') and name.endswith(')')),
                not (len(name) == 3 and name.endswith('.')),
            ])
        ]

        if len(name_parts) == 2:
            if ',' in name_parts[0]:  # Last, First
                formatted_name = ' '.join(name_parts).title()
            elif '.' not in name_parts[0] and '.' not in name_parts[1]:  # First Last
                formatted_name = f'{name_parts[1]}, {name_parts[0]}'.title()
        elif len(name_parts) == 3:
            if '.' in name_parts[0]:  # F_Initial Middle Last
                formatted_name = f'{name_parts[2]}, {name_parts[0]} {name_parts[1]}'.title()
            elif '.' in name_parts[1]:  # First M_Initial Last
                formatted_name = f'{name_parts[2]}, {name_parts[0]} {name_parts[1]}'.title()
        else:
            formatted_name = ' '.join(name_parts).title()

        return formatted_name

    @staticmethod
    def numerical(field_text: str) -> float:
        n = 0.0
        digits = [c for c in field_text if c.isdigit() or c == '.']
        if digits:
            try:
                n = float(''.join(digits))
            except ValueError:
                pass
        return n

if __name__ == '__main__':
    pass
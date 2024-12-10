import unicodedata
from utils import play_alert

# Placeholder Name: John Q. Public

def generate_name_parts_list(raw_name: str) -> list[str]:
    return [
        name_part.strip() for name_part in raw_name.split()
        if name_part and name_part not in Formatting.TITLES and not (
            (name_part.startswith('"') and name_part.endswith('"')) or  # ['John', '"Johnny"', 'Public']
            (name_part.startswith('(') and name_part.endswith(')')) or  # ['John', '(Johnny)', 'Public']
            (len(name_part) == 3 and name_part.endswith('.')) or  # titles that may not be included in Formatting.TITLES
            (len(name_part) == 2 and name_part.endswith('.')) or  # ['John', 'Q.', 'Public'] or ['J.', 'Public']
            (len(name_part) == 1)  # ['John', 'Q', 'Public'] or ['J', 'Public'] or ['John', 'P']
        )
        ]

def format_name(original_name: str) -> tuple[str]:
    play_alert()

    max_attempts: int = 3
    for _ in range(max_attempts):
        print(
            f'Enter "{original_name}" formatted as "FIRST LAST"\n'
            'Enter 0 to skip.'
            )
        user_input: str = input('>>> ').strip()
        print()

        if user_input == '0':
            raise ValueError(f'Name not recognized: {original_name}')

        split_name: list[str] = user_input.split()
        if len(split_name) == 2:
            first_name, last_name = split_name
            return last_name, first_name

        print('Invalid name format.\n')

    raise ValueError(f'Invalid name format: {original_name}')

class Formatting:
    TITLES = {'Dr.', 'Mr.', 'Mrs.', 'Miss.', 'Ms.', 'Prof.', 'Ph.D', 
              'Dr', 'Mr', 'Mrs', 'Miss', 'Ms', 'Prof', 'PhD'}

    @staticmethod
    def justification(field_text: str) -> str:
        if not field_text:
            return ''

        justif_str = unicodedata.normalize('NFKD', field_text).encode('ascii', 'ignore').decode('ascii')
        justif_str = justif_str.replace('"', "'").replace('  ', ' ')
        return f'"{justif_str}"'

    @staticmethod
    def name(raw_name: str) -> str:
        if not raw_name:
            return ''

        name_parts: list[str] = generate_name_parts_list(raw_name)

        last_name, first_name = '', ''

        if len(name_parts) == 2:
            if ',' in name_parts[0]:  # name_parts = ['Public,', 'John']
                last_name, first_name = name_parts[0].replace(',',''), name_parts[1]
            else:     
                last_name, first_name = name_parts[1], name_parts[0]          # not ['J.','Public'] or ['John', 'P.']
            
        elif len(name_parts) == 3:
            min_len: int = min(len(name_part) for name_part in name_parts)
            contains_prd: bool = any('.' in name_part for name_part in name_parts)
            if min_len >= 3 and not contains_prd:
                last_name, first_name = name_parts[2], name_parts[0]

        if not all([last_name, first_name]):
            last_name,first_name = format_name(raw_name)
        
        return ', '.join([last_name,first_name]).title()



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
    print(format_name('j strong'))

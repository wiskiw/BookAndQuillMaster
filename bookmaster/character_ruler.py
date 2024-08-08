import re

from bookmaster.model.text_unit import TextUnit


class McCharRuler:
    colors_codes = {
        "§0": "black",
        "§1": "dark_blue",
        "§2": "dark_green",
        "§3": "dark_aqua",
        "§4": "dark_red",
        "§5": "dark_purple",
        "§6": "gold",
        "§7": "gray",
        "§8": "dark_gray",
        "§9": "blue",
        "§a": "green",
        "§b": "aqua",
        "§c": "red",
        "§d": "light_purple",
        "§e": "yellow",
        "§f": "white",
    }

    formatting_codes = {
        "§k": "obfuscated",
        "§l": "bold",
        "§m": "strikethrough",
        "§n": "underline",
        "§o": "italic",
        "§r": "reset",
    }

    between_chars_width = 1

    char_to_width_dict: dict[str, int]

    def __init__(self, char_width_dict_file: str):
        self.char_to_width_dict = McCharRuler.__read_char_to_width_dict(char_width_dict_file)
        print(f"McCharRuler size: {len(self.char_to_width_dict)}")

    def get_width(self, text: str):
        clean_text = self.__remote_codes(text)

        if len(clean_text) == 0:
            return 0

        text_width = 0

        for char in clean_text:
            if char not in self.char_to_width_dict:
                raise Exception(f'Width is missing for character \'{char}\'')

            char_width = self.char_to_width_dict[char]
            text_width += char_width

        all_spaces_width = max(len(clean_text) - 1, 0) * self.between_chars_width
        return text_width + all_spaces_width

    def get_width_of_text_unit(self, text_unit: TextUnit) -> int:
        return self.get_width(text=text_unit.get_raw_text())

    def get_width_of_text_units(self, text_unit_list: list[TextUnit]) -> int:
        all_units_width = 0
        for text_unit in text_unit_list:
            unit_width = self.get_width_of_text_unit(text_unit=text_unit)
            all_units_width += unit_width

        all_spaces_width = max(len(text_unit_list) - 1, 0) * self.between_chars_width
        return all_units_width + all_spaces_width

    def __remote_codes(self, text: str) -> str:
        clean_text = text

        for color_code in self.colors_codes.keys():
            clean_text = clean_text.replace(color_code, '')

        for formatting_code in self.formatting_codes.keys():
            clean_text = clean_text.replace(formatting_code, '')

        return clean_text

    @staticmethod
    def __read_char_to_width_dict(char_width_dict_file: str) -> dict:
        char_width_file = open(char_width_dict_file, 'r')
        char_width_lines = char_width_file.readlines()
        tab_char = chr(9)
        comments_regex = r"\/\/.*"

        char_to_width_dict = {}

        line_number = 0
        # Strips the newline character
        for char_width_line in char_width_lines:
            line_number += 1

            # remove comments
            char_width_line = re.sub(comments_regex, "", char_width_line)

            # skip empty lines
            if len(char_width_line.strip()) == 0:
                continue

            char_width_entities = char_width_line.rstrip().split(tab_char)
            if len(char_width_entities) == 2:
                value = char_width_entities[0]
                if len(value) > 1 and value.startswith("U+"):
                    char = McCharRuler.__unicode_code_point_to_char(value)
                elif len(value) == 1:
                    char = value
                else:
                    print(f"Unable to read char width at line {line_number}")
                    continue

                width = int(char_width_entities[1])
                char_to_width_dict[char] = width
            else:
                print(f"Wrong number of entities at line {line_number}")

        # printing
        # for key, value in char_to_width_dict.items():
        #     print('%s: %s' % (key, value))

        return char_to_width_dict

    @staticmethod
    def __unicode_code_point_to_char(code_point):
        # Step 1: Remove the "U+" prefix
        hex_value = code_point[2:]

        # Step 2: Convert the hexadecimal string to an integer
        int_value = int(hex_value, 16)

        # Step 3: Use chr to get the character
        character = chr(int_value)

        # print(character)  # Output: ;
        return character

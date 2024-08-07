from text_unit_reader import TextUnitReader
from text_container import McCharRuler, TextContainerWriter

from model.text_root_unit import *
import json5
import os

char_width_dict_file = 'char_width.txt'
export_text_unit_file = './text_units.json5'
input_file = './input.txt'
output_file = './output.txt'


def export_text_unit(text_unit: TextUnit):
    unit_dict = text_unit.get_dict()
    save_json5(unit_dict, export_text_unit_file)


def save_json5(json_data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        json5.dump(json_data, file, ensure_ascii=False, indent=4)


def read_inout_file():
    with open(input_file, 'r') as file:
        text_content = file.read()
        return str(text_content)


def write_output_file(content):
    f = open(output_file, "w")
    f.write(content)
    f.close()


def unicode_code_point_to_char(code_point):
    # Step 1: Remove the "U+" prefix
    hex_value = code_point[2:]

    # Step 2: Convert the hexadecimal string to an integer
    int_value = int(hex_value, 16)

    # Step 3: Use chr to get the character
    character = chr(int_value)

    # print(character)  # Output: ;
    return character


def read_char_to_width_dict():
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
                char = unicode_code_point_to_char(value)
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


def run():
    # reading input
    raw_text = read_inout_file()

    # parsing text into units
    root_unit = TextRootUnit(raw_text)

    # export text units tree
    export_text_unit(root_unit)

    # creating a rulet
    ruler_dict = read_char_to_width_dict()
    print(f"ruler_dict len={len(ruler_dict)}")
    ruler = McCharRuler(char_to_width_dict=ruler_dict)

    text_unit_reader = TextUnitReader(text_unit=root_unit)
    text_container_writer = TextContainerWriter(reader=text_unit_reader, ruler=ruler)
    text_container = text_container_writer.write()

    # writing output
    write_output_file(content=text_container.get_pretty_str())
    print(text_container.get_pretty_str())


if __name__ == '__main__':
    run()


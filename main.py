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


def run():
    # reading input
    raw_text = read_inout_file()

    # parsing text into units
    root_unit = TextRootUnit(raw_text)

    # export text units tree
    export_text_unit(root_unit)

    text_unit_reader = TextUnitReader(text_unit=root_unit)
    ruler = McCharRuler(char_width_dict_file=char_width_dict_file)
    text_container_writer = TextContainerWriter(reader=text_unit_reader, ruler=ruler)
    text_container = text_container_writer.write()

    # writing output
    write_output_file(content=text_container.get_pretty_str())
    print(text_container.get_pretty_str())


if __name__ == '__main__':
    run()

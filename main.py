from debug_utils import *
from model.text_root_unit import *
from text_container import McCharRuler, TextContainerWriter
from text_unit_reader import TextUnitReader

char_width_dict_file = 'char_width.txt'
export_text_unit_file = './text_units.json5'
input_file = './input.txt'
output_file = './output.txt'


def run():
    # reading input
    raw_text = read_inout_file(file_path=input_file)

    # parsing text into units
    root_unit = TextRootUnit(raw_text)

    # export text units tree
    export_text_unit(file_path=export_text_unit_file, text_unit=root_unit)

    text_unit_reader = TextUnitReader(text_unit=root_unit)
    ruler = McCharRuler(char_width_dict_file=char_width_dict_file)
    text_container_writer = TextContainerWriter(reader=text_unit_reader, ruler=ruler)
    book = text_container_writer.write()

    # writing output
    write_output_file(file_path=output_file, content=book.get_pretty_str())
    print(book.get_pretty_str())


if __name__ == '__main__':
    run()

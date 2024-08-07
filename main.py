from book_formatter import McBookFormatter
from io_utils import *
from model.text_root_unit import *
from text_container import McCharRuler, BookWriter
from text_unit_reader import TextUnitReader

char_width_dict_file = 'char_width.txt'
export_text_unit_file = './debug/text_units.json5'
input_file = './debug/input.txt'


def run():
    # reading input
    raw_text = read_file(file_path=input_file)

    # parsing text into units
    root_unit = TextRootUnit(raw_text)

    # export text units tree
    export_text_unit(file_path=export_text_unit_file, text_unit=root_unit)

    text_unit_reader = TextUnitReader(text_unit=root_unit)
    ruler = McCharRuler(char_width_dict_file=char_width_dict_file)
    text_container_writer = BookWriter(reader=text_unit_reader, ruler=ruler)
    book = text_container_writer.write()

    # writing output
    book_formatter = McBookFormatter(book)
    write_json('./out/book_json.json', book_formatter.to_json())
    write_file('./out/book_pretty.txt', book_formatter.to_pretty_text())

    print(f"Written a book with {len(book.get_pages())} page(s)")


if __name__ == '__main__':
    run()

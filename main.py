from bookmaster.book_formatter import McBookFormatter
from bookmaster.book_writer import BookWriter
from other.book_utils import move_to_bookcopy_dir
from other.io_utils import *
from bookmaster.model.text_root_unit import *
from bookmaster.text_container import McCharRuler
from bookmaster.text_unit_reader import TextUnitReader

char_width_dict_file = 'bookmaster/char_width.txt'
export_text_unit_file = './debug/text_units.json5'
input_file = './debug/input.txt'


def run():
    # reading input
    raw_text = read_file(file_path=input_file)

    # parsing text into units
    root_unit = TextRootUnit(raw_text)
    export_text_unit(file_path=export_text_unit_file, text_unit=root_unit)

    book_writer = BookWriter(
        reader=TextUnitReader(text_unit=root_unit),
        ruler=McCharRuler(char_width_dict_file=char_width_dict_file),
    )
    book = book_writer.write()
    print(f"Written a book with {len(book.get_pages())} page(s)")

    # writing output
    book_formatter = McBookFormatter(book)
    write_json('./debug/book_json.json', book_formatter.to_json())
    write_file('./debug/book_pretty.txt', book_formatter.to_pretty_text())

    move_to_bookcopy_dir('./debug/book_json.json', 'book_json.json')


if __name__ == '__main__':
    run()

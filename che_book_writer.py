#!/usr/bin/env python3
import arrow

from bookmaster.book_formatter import McBookFormatter
from bookmaster.book_writer import BookWriter
from bookmaster.character_ruler import McCharRuler
from bookmaster.model.text_root_unit import TextRootUnit
from bookmaster.text_container import McBook
from bookmaster.text_unit_reader import TextUnitReader
from other.book_utils import fill_up_raw_template, move_to_bookcopy_dir
from other.io_utils import read_file, write_json, export_text_unit, write_file
from other.telegram.tg_tool import *
from emoji import distinct_emoji_list
from transliterate import translit
import asyncio
import sys

# Run command with arguments example:
# python3 joke_b.py <episode_name> <last_message_id> <number of messages>
# python3 che_book_writer.py первый 20472 16

channel_username = '@jqofa'
src_dir = 'content/che'

max_pages_per_joke = 2
last_page_min_lines = 4

ruler = McCharRuler(char_width_dict_file='bookmaster/char_width.txt')


def remove_substr_start_end(s, start, end):
    return s[:start] + s[end + 1:]


def clear_message(message):
    result = message.message

    return result \
        .strip() \
        .replace('  ', ' ') \
        .replace(' ', ' ')


def is_message_valid(message) -> bool:
    if message.message is None:
        return False

    clean_message = clear_message(message)

    has_no_link = message.entities is None or len(message.entities) == 0
    its_no_reply = message.reply_markup is None
    has_no_emoji = len(distinct_emoji_list(clean_message)) == 0
    has_no_photo = message.media is None

    if not has_no_link or not its_no_reply or not has_no_emoji or not has_no_photo:
        return False

    raw_page_template = read_raw_page_template()
    raw_page_content = build_raw_page_content(raw_page_template, message)

    root_unit = TextRootUnit(raw_page_content)
    text_unit_reader = TextUnitReader(text_unit=root_unit)

    try:
        page_book = BookWriter(reader=text_unit_reader, ruler=ruler).write()
        fit_in_page_limit = len(page_book.get_pages()) <= max_pages_per_joke

        last_page = page_book.get_page(len(page_book.get_pages()) - 1)
        last_page_has_enough_lines = len(last_page.get_lines()) >= last_page_min_lines

        return fit_in_page_limit and last_page_has_enough_lines
    except ValueError:
        return False


def build_raw_page_content(raw_quote_template: str, message):
    quote_dict = {
        'content': clear_message(message),
    }
    return fill_up_raw_template(raw_template=raw_quote_template, args_dictionary=quote_dict)


def read_raw_page_template():
    return read_file(f"{src_dir}/raw_page_template.txt")


def build_raw_content_list(message_list) -> list[str]:
    raw_quote_template = read_raw_page_template()

    raw_page_content_list = []

    for message in message_list:
        raw_page_content = build_raw_page_content(raw_quote_template, message)
        raw_page_content_list.append(raw_page_content)

    return raw_page_content_list


def create_book(raw_content: str) -> McBook | None:
    # parsing text into units
    root_unit = TextRootUnit(raw_content)
    export_text_unit(file_path='./debug/text_units.json5', text_unit=root_unit)

    # writing debug output
    write_file(f'{src_dir}/raw_content.txt', raw_content)

    text_unit_reader = TextUnitReader(text_unit=root_unit)
    try:
        book = BookWriter(reader=text_unit_reader, ruler=ruler).write()
        return book
    except ValueError:
        return None


async def __main__(cmd_args):
    required_args_count = 3
    arg_episode_name = 'unknown'
    arg_offset_id = 0
    arg_count = 3

    if len(cmd_args) == required_args_count + 1:
        arg_episode_name = cmd_args[1]
        arg_offset_id = int(cmd_args[2])
        arg_count = int(cmd_args[3])
    else:
        print('Please specify: <episode_name> <min_id> <count>')
        return

    ranged_messages = await load_filtered_messages(
        channel_username=channel_username,
        offset_id=arg_offset_id,
        count=arg_count,
        filter_valid=lambda item: list(filter(is_message_valid, item)),
        requrest_size=100,
    )

    args_dictionary = {
        'episode_name': arg_episode_name,
        'date': arrow.now().shift(days=-1).format('DD.MM.YYYY'),
        'raw_content_list': '\n'.join(build_raw_content_list(ranged_messages.messages)),
    }

    # create raw content
    raw_template = read_file(f"{src_dir}/raw_template.txt")
    raw_content = fill_up_raw_template(raw_template=raw_template, args_dictionary=args_dictionary)

    # creating a book object
    book = create_book(raw_content=raw_content)
    if book is None:
        print(f"ERROR unable to create book")
        return

    book.set_title(title=f'ЧЕ? - {arg_episode_name}')

    # saving json book
    book_formatter = McBookFormatter(book)
    translit_episode_name = translit(arg_episode_name, 'ru', reversed=True)
    destination_file_name = \
        f"che_{translit_episode_name}_{ranged_messages.id_range_start}-{ranged_messages.id_range_end}.json"

    destination_file_path = f"{src_dir}/{destination_file_name}"
    write_json(destination_file_path, book_formatter.to_json())
    print(f"Written a book with {len(book.get_pages())} page(s)")

    move_to_bookcopy_dir(destination_file_path, destination_file_name)


asyncio.run(__main__(sys.argv))

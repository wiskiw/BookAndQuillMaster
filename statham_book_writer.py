#!/usr/bin/env python3
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
import asyncio
import sys
import arrow

# Run command with arguments example:
# python3 statham_book_writer.py <episode> <last_message_id> <number_of_messages>
# python3 statham_book_writer.py 0 5900 25

channel_username = '@statham_jason'
src_dir = 'content/statham'

ruler = McCharRuler(char_width_dict_file='bookmaster/char_width.txt')


def remove_substr_start_end(s, start, end):
    return s[:start] + s[end + 1:]


def clear_message(message):
    result = message.message

    # remove original signature from the message
    if message.entities is not None and len(message.entities) > 0:
        author_name_entity_cashtag = message.entities[0]
        result = remove_substr_start_end(result, author_name_entity_cashtag.offset,
                                         author_name_entity_cashtag.offset + author_name_entity_cashtag.length)

    return result \
        .strip() \
        .replace('  ', ' ')


def is_message_valid(message) -> bool:
    # message.entities == 1 - only for © Джейсон Стетхем link
    has_one_link = message.entities is None or len(message.entities) == 1
    has_no_replies = message.reply_markup is None

    clean_message = clear_message(message)
    has_no_emoji = len(distinct_emoji_list(clean_message)) == 0
    if not has_one_link or not has_no_replies or not has_no_emoji:
        return False

    raw_quote_template = read_raw_quote_template()
    raw_quote_content = build_raw_quote_content(raw_quote_template, message)

    root_unit = TextRootUnit(raw_quote_content)
    text_unit_reader = TextUnitReader(text_unit=root_unit)
    quote_book = BookWriter(reader=text_unit_reader, ruler=ruler).write()

    fit_in_single_page = len(quote_book.get_pages()) == 1
    return fit_in_single_page


def build_raw_quote_content(raw_quote_template: str, message):
    quote_dict = {
        'quote': clear_message(message),
        'author': "Джейсон Стетхем"
    }
    return fill_up_raw_template(raw_template=raw_quote_template, args_dictionary=quote_dict)


def read_raw_quote_template():
    return read_file(f"{src_dir}/raw_quote_template.txt")


def build_raw_content_list(message_list) -> list[str]:
    raw_quote_template = read_raw_quote_template()

    raw_quote_content_list = []

    for message in message_list:
        raw_quote_content = build_raw_quote_content(raw_quote_template, message)
        raw_quote_content_list.append(raw_quote_content)

    return raw_quote_content_list


def create_book(raw_content: str) -> McBook:
    # parsing text into units
    root_unit = TextRootUnit(raw_content)
    export_text_unit(file_path='./debug/text_units.json5', text_unit=root_unit)

    # writing debug output
    write_file(f'{src_dir}/raw_content.txt', raw_content)

    text_unit_reader = TextUnitReader(text_unit=root_unit)
    return BookWriter(reader=text_unit_reader, ruler=ruler).write()


async def __main__(cmd_args):
    required_args_count = 3
    arg_episode = 0
    arg_offset_id = 0
    arg_count = 3

    if len(cmd_args) == required_args_count + 1:
        arg_episode = int(cmd_args[1])
        arg_offset_id = int(cmd_args[2])
        arg_count = int(cmd_args[3])
    else:
        print('Please specify: <episode> <min_id> <count>')
        return

    ranged_messages = await load_filtered_messages(
        channel_username=channel_username,
        offset_id=arg_offset_id,
        count=arg_count,
        filter_valid=lambda item: list(filter(is_message_valid, item)),
    )

    args_dictionary = {
        'episode': arg_episode,
        'quite_raw_content_list': '\n'.join(build_raw_content_list(ranged_messages.messages)),
        'date': arrow.now().shift(days=-1).format('DD.MM.YYYY'),
    }

    # create raw content
    raw_template = read_file(f"{src_dir}/raw_template.txt")
    raw_content = fill_up_raw_template(raw_template=raw_template, args_dictionary=args_dictionary)

    # creating a book object
    book = create_book(raw_content=raw_content)
    book.set_title(title=f'Цитаты Дж.Стетхема №{arg_episode}')

    # saving json book
    book_formatter = McBookFormatter(book)
    destination_file_name = \
        f"statham_{arg_episode}_{ranged_messages.id_range_start}-{ranged_messages.id_range_end}.json"

    destination_file_path = f"{src_dir}/{destination_file_name}"
    write_json(destination_file_path, book_formatter.to_json())
    print(f"Written a book with {len(book.get_pages())} page(s)")

    move_to_bookcopy_dir(destination_file_path, destination_file_name)


asyncio.run(__main__(sys.argv))

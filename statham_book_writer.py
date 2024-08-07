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
import asyncio
import sys

channel_username = '@statham_jason'
src_dir = 'content/statham'
char_width_dict_file = 'bookmaster/char_width.txt'

load_message_count = 30
max_message_len = 232
max_line_breaks_per_message = 5
min_reactions_count = 400


def remove_substr_start_end(s, start, end):
    return s[:start] + s[end + 1:]


def clear_message_text(message):
    result = message.message

    # remove original signature from the message
    if message.entities is not None and len(message.entities) > 0:
        author_name_entity_cashtag = message.entities[0]
        result = remove_substr_start_end(result, author_name_entity_cashtag.offset,
                                         author_name_entity_cashtag.offset + author_name_entity_cashtag.length)

    return result \
        .strip() \
        .replace('"', '\\"') \
        .replace('  ', ' ')


def build_raw_content_list(message_list) -> list[str]:
    raw_quote_template = read_file(f"{src_dir}/raw_quote_template.txt")

    raw_content_list = []

    for message in message_list:
        page_dick = {
            'quote': clear_message_text(message),
            'author': "Джейсон Стетхем"
        }
        raw_content = fill_up_raw_template(raw_template=raw_quote_template, args_dictionary=page_dick)
        raw_content_list.append(raw_content)

    return raw_content_list


def is_message_valid(message):
    message_text = message.message

    # message.entities) == 1 - only for © Джейсон Стетхем link
    return message_text is not None \
        and message_text.count('\n') <= max_line_breaks_per_message \
        and len(message_text) <= max_message_len \
        and message.reply_markup == None \
        and (message.entities is None or len(message.entities) == 1)  # entity (link) onlin on it's own


def create_book(raw_content: str) -> McBook:
    # parsing text into units
    root_unit = TextRootUnit(raw_content)
    export_text_unit(file_path='./debug/text_units.json5', text_unit=root_unit)

    # writing debug output
    write_file(f'{src_dir}/raw_content.txt', raw_content)

    text_unit_reader = TextUnitReader(text_unit=root_unit)
    ruler = McCharRuler(char_width_dict_file=char_width_dict_file)
    text_container_writer = BookWriter(reader=text_unit_reader, ruler=ruler)
    return text_container_writer.write()


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

    messages = await load_filtered_messages(
        channel_username=channel_username,
        offset_id=arg_offset_id,
        count=arg_count,
        filter_valid=lambda item: list(filter(is_message_valid, item)),
    )

    args_dictionary = {
        'episode': arg_episode,
        'content_list': '\n'.join(build_raw_content_list(messages)),
    }

    # create raw content
    raw_template = read_file(f"{src_dir}/raw_template.txt")
    raw_content = fill_up_raw_template(raw_template=raw_template, args_dictionary=args_dictionary)

    # creating a book object
    book = create_book(raw_content=raw_content)

    # saving json book
    book_formatter = McBookFormatter(book)
    destination_file_name = f"statham_{arg_episode}.json"
    destination_file_path = f"{src_dir}/{destination_file_name}"
    write_json(destination_file_path, book_formatter.to_json())
    print(f"Written a book with {len(book.get_pages())} page(s)")

    move_to_bookcopy_dir(destination_file_path, destination_file_name)


asyncio.run(__main__(sys.argv))

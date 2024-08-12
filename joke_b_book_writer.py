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

# Run command with arguments example:
# python3 joke_b.py <episode> <last_message_id> <number of messages>
# python3 joke_b.py 0 3200 27

src_dir = 'content/joke_b'
channel_username = '@baneksru'

min_reactions_count = 400
max_pages_per_joke = 2
last_page_min_lines = 3

ruler = McCharRuler(char_width_dict_file='bookmaster/char_width.txt')


def clear_message(message):
    message_text = message.message
    return message_text.strip()


def get_message_reactions_count(message):
    reactions_counter = 0

    for rc in message.reactions.results:
        reactions_counter += rc.count

    return reactions_counter


def is_message_valid(message) -> bool:
    reactions_counter = get_message_reactions_count(message)
    has_one_link = message.entities is None or len(message.entities) == 1
    has_enough_reactions = reactions_counter >= min_reactions_count
    has_no_replies = message.reply_markup is None
    if not has_enough_reactions or message.message is None or not has_one_link or not has_no_replies:
        return False

    raw_joke_template = read_raw_joke_template()
    raw_joke_content = build_raw_joke_content(
        raw_template=raw_joke_template,
        message=message,
        joke_number=123,  # any number just to generate pages for validation
    )

    root_unit = TextRootUnit(raw_joke_content)
    text_unit_reader = TextUnitReader(text_unit=root_unit)
    joke_book = BookWriter(reader=text_unit_reader, ruler=ruler).write()

    fit_in_page_limit = len(joke_book.get_pages()) <= max_pages_per_joke

    last_page = joke_book.get_page(len(joke_book.get_pages()) - 1)
    last_page_has_enough_lines = len(last_page.get_lines()) >= last_page_min_lines
    return fit_in_page_limit and last_page_has_enough_lines


def read_raw_joke_template():
    return read_file(f"{src_dir}/raw_joke_template.txt")


def build_raw_joke_content(raw_template: str, message, joke_number: int):
    quote_dict = {
        'joke': clear_message(message),
        'joke_number': joke_number,
    }
    return fill_up_raw_template(raw_template=raw_template, args_dictionary=quote_dict)


def build_raw_content_list(message_list) -> list[str]:
    raw_joke_template = read_raw_joke_template()

    raw_joke_content_list = []
    message_index = 0
    for message in message_list:
        raw_joke_content = build_raw_joke_content(
            raw_template=raw_joke_template,
            message=message,
            joke_number=message_index + 1,
        )
        raw_joke_content_list.append(raw_joke_content)
        message_index += 1

    return raw_joke_content_list


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
        'joke_raw_content_list': '\n'.join(build_raw_content_list(ranged_messages.messages)),
    }

    # create raw content
    raw_template = read_file(f"{src_dir}/raw_template.txt")
    raw_content = fill_up_raw_template(raw_template=raw_template, args_dictionary=args_dictionary)

    # creating a book object
    book = create_book(raw_content=raw_content)
    book.set_title(title=f'Анекдоты №{arg_episode}')

    # saving json book
    book_formatter = McBookFormatter(book)
    destination_file_name = f"joke_b_{arg_episode}_{ranged_messages.id_range_start}-{ranged_messages.id_range_end}.json"
    destination_file_path = f"{src_dir}/{destination_file_name}"
    write_json(destination_file_path, book_formatter.to_json())
    # write_file('./debug/book_pretty.txt', book_formatter.to_pretty_text())
    print(f"Written a book with {len(book.get_pages())} page(s)")

    move_to_bookcopy_dir(destination_file_path, destination_file_name)


asyncio.run(__main__(sys.argv))

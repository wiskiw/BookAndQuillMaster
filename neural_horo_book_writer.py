#!/usr/bin/env python3
import re

from bookmaster.book_formatter import McBookFormatter
from bookmaster.book_writer import BookWriter
from other.book_utils import *
from bookmaster.character_ruler import McCharRuler
from other.io_utils import write_json, write_file, read_file, export_text_unit
from bookmaster.model.text_root_unit import TextRootUnit
from bookmaster.text_container import McBook
from bookmaster.text_unit_reader import TextUnitReader
from other.telegram.tg_tool import *
import asyncio
import sys

src_dir = 'content/neural_horo'
channel_username = '@neural_horo'
char_width_dict_file = 'bookmaster/char_width.txt'

HORO_SIGN_KEY_ARIES = 'aries'
HORO_SIGN_KEY_TAURUS = 'taurus'
HORO_SIGN_KEY_GEMINI = 'gemini'
HORO_SIGN_KEY_CANCER = 'cancer'
HORO_SIGN_KEY_LEO = 'leo'
HORO_SIGN_KEY_VIRGO = 'virgo'
HORO_SIGN_KEY_LIBRA = 'libra'
HORO_SIGN_KEY_SCORPIO = 'scorpio'
HORO_SIGN_KEY_SAGITTARIUS = 'sagittarius'
HORO_SIGN_KEY_CAPRICORN = 'capricorn'
HORO_SIGN_KEY_AQUARIUS = 'aquarius'
HORO_SIGN_KEY_PISCES = 'pisces'

HOROSCOPE_GROUP_KEY = 'horoscope'
ZODIAC_SIGNS_PARSE_DICT = {
    HORO_SIGN_KEY_ARIES: re.compile(r'Овен:\s*(?P<%s>.*)\n' % HOROSCOPE_GROUP_KEY),
    HORO_SIGN_KEY_TAURUS: re.compile(r'Телец:\s*(?P<%s>.*)\n' % HOROSCOPE_GROUP_KEY),
    HORO_SIGN_KEY_GEMINI: re.compile(r'Близнецы:\s*(?P<%s>.*)\n' % HOROSCOPE_GROUP_KEY),
    HORO_SIGN_KEY_CANCER: re.compile(r'Рак:\s*(?P<%s>.*)\n' % HOROSCOPE_GROUP_KEY),
    HORO_SIGN_KEY_LEO: re.compile(r'Лев:\s*(?P<%s>.*)\n' % HOROSCOPE_GROUP_KEY),
    HORO_SIGN_KEY_VIRGO: re.compile(r'Дева:\s*(?P<%s>.*)\n' % HOROSCOPE_GROUP_KEY),
    HORO_SIGN_KEY_LIBRA: re.compile(r'Весы:\s*(?P<%s>.*)\n' % HOROSCOPE_GROUP_KEY),
    HORO_SIGN_KEY_SCORPIO: re.compile(r'Скорпион:\s*(?P<%s>.*)\n' % HOROSCOPE_GROUP_KEY),
    HORO_SIGN_KEY_SAGITTARIUS: re.compile(r'Стрелец:\s*(?P<%s>.*)\n' % HOROSCOPE_GROUP_KEY),
    HORO_SIGN_KEY_CAPRICORN: re.compile(r'Козерог:\s*(?P<%s>.*)\n' % HOROSCOPE_GROUP_KEY),
    HORO_SIGN_KEY_AQUARIUS: re.compile(r'Водолей:\s*(?P<%s>.*)\n' % HOROSCOPE_GROUP_KEY),
    HORO_SIGN_KEY_PISCES: re.compile(r'Рыбы:\s*(?P<%s>.*)' % HOROSCOPE_GROUP_KEY),  # no line break at the end
}


async def load_message(message_id):
    # Get the channel entity
    await client.start()
    channel = await client.get_entity(channel_username)
    return await client.get_messages(channel, ids=message_id)


def parse_message(content, regex):
    match = regex.search(content)
    if match:
        return match.group(HOROSCOPE_GROUP_KEY)
    return None


async def load_neural_scope_map(message_id: int) -> dict:
    message = await load_message(message_id=message_id)

    neural_scope_map = {}
    for horo_sign, regex in ZODIAC_SIGNS_PARSE_DICT.items():
        neural_horo = parse_message(message.message, regex)
        if neural_horo is not None:
            neural_scope_map[horo_sign] = neural_horo
        else:
            raise Exception(f"Failed to parse message '{message.message}'")

    return neural_scope_map


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
    required_args_count = 2
    arg_message_id = 0
    arg_week_date = 0

    if len(cmd_args) == required_args_count + 1:
        arg_message_id = int(cmd_args[1])
        arg_week_date = cmd_args[2]
    else:
        print('Please specify: <message_id> <week_date>')
        return

    args_dictionary = {
        'weekDate': arg_week_date,
    }

    neural_scope_map = await load_neural_scope_map(message_id=arg_message_id)
    for horo_sign_key, horo_sign_value in neural_scope_map.items():
        args_dictionary[horo_sign_key] = horo_sign_value

    # create raw content
    raw_template = read_file(f"{src_dir}/raw_template.txt")
    raw_content = fill_up_raw_template(raw_template=raw_template, args_dictionary=args_dictionary)

    # creating a book object
    book = create_book(raw_content=raw_content)

    # saving json book
    book_formatter = McBookFormatter(book)
    destination_file_name = f"neural_horo_{arg_message_id}_{arg_week_date}.json"
    destination_file_path = f"{src_dir}/{destination_file_name}"
    write_json(destination_file_path, book_formatter.to_json())
    print(f"Written a book with {len(book.get_pages())} page(s)")

    move_to_bookcopy_dir(destination_file_path, destination_file_name)


asyncio.run(__main__(sys.argv))

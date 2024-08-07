#!/usr/bin/env python3
import time
from dataclasses import dataclass

from telethon import TelegramClient

from other.telegram.tg_credits import API_ID, API_HASH

client = TelegramClient('telegram', API_ID, API_HASH)


async def load_messages(channel_username, offset, limit):
    # Connect to the client
    await client.start()

    # Get the channel entity
    channel = await client.get_entity(channel_username)
    message_items = await client.get_messages(channel, add_offset=offset, limit=limit)

    messages = list(map(lambda item: item.message, message_items))
    messages = list(filter(lambda message: message is not None, messages))
    messages = messages[:limit]

    print(f"Fetched {len(messages)} messages.")
    return messages


def get_message_with_details(message_item):
    reactions_count = 0
    for rc in message_item.reactions.results:
        reactions_count += rc.count

    return {
        'message': message_item.message,
        'reactions_count': reactions_count,
        'id': message_item.id
    }


async def load_messages_with_details(channel_username, offset_id, limit):
    # Connect to the client
    await client.start()

    # Get the channel entity
    channel = await client.get_entity(channel_username)
    messages = await client.get_messages(channel, offset_id=offset_id, limit=limit)

    messages = list(filter(lambda message: message.entities is None or len(message.entities) == 0, messages))
    messages = list(map(get_message_with_details, messages))
    messages = list(filter(lambda message: message['message'] is not None, messages))

    return messages


async def load_filtered_messages(channel_username, offset_id, count, filter_valid) -> 'FilteredMessages':
    request_limit = 20

    # Get the channel entity
    await client.start()
    channel = await client.get_entity(channel_username)

    first_loaded_message = None
    last_loaded_message = None

    request_index = 0
    valid_messages = []

    while True:
        request_index += 1
        print(f"Loading {request_limit} messages with start offset id {offset_id}, request {request_index} ")

        # Loading messages
        messages = await client.get_messages(channel, offset_id=offset_id, limit=request_limit)

        # print(f"raw messages:{messages}")
        valid_messages = valid_messages + filter_valid(messages)

        if first_loaded_message is None:
            first_loaded_message = messages[0]
        last_loaded_message = messages[len(messages) - 1]

        if len(valid_messages) >= count:
            break

        # increment cycle values
        offset_id = last_loaded_message.id
        time.sleep(0.3)  # seconds

    valid_messages = valid_messages[:count]
    print(
        f"Found {len(valid_messages)} valid messages in {request_index + 1} requests. "
        f"Used id range: {last_loaded_message.id}-{first_loaded_message.id}."
    )

    return RangedMessages(
        id_range_start=last_loaded_message.id,
        id_range_end=first_loaded_message.id,
        messages=valid_messages
    )


@dataclass
class RangedMessages:
    id_range_start: int
    id_range_end: int
    messages: list

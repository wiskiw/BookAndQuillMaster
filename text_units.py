import re
import string
from enum import Enum
from typing import List, Union
from abc import ABC


class FormatFlag(Enum):
    START_OF_PARAGRAPH = 'START_OF_PARAGRAPH'
    START_OF_SENTENCE = 'START_OF_SENTENCE'


class TextUnit(ABC):

    def _parse_sub_units(self, raw_text: str) -> list['TextUnit']:
        return []

    def __init__(self, raw_text: str, format_flags=None):
        if format_flags is None:
            format_flags = []

        self.__raw_text: str = raw_text
        self.__format_flags: list[FormatFlag] = format_flags
        self.__sub_units: List[TextUnit] = self._parse_sub_units(raw_text=raw_text)

    def __str__(self):
        return f"{type(self).__name__}({self.__sub_units if self.__sub_units else self.__raw_text})"

    def __repr__(self):
        return str(self)

    def get_raw_text(self) -> str:
        return self.__raw_text

    def get_format_flags(self) -> list[FormatFlag]:
        return self.__format_flags

    def get_sub_units(self) -> list['TextUnit']:
        return self.__sub_units

    # address = [] - leads to self
    # address = [0] - leads to first sub-unit
    # address = [0, 1] - leads to second sub-unit of self sub-unit
    # if address out or range -> None
    def get_by_address(self, address: List[int]) -> Union['TextUnit', None]:
        if len(address) == 0:
            return self

        sub_unit_index = address[0]
        if sub_unit_index < len(self.get_sub_units()):
            sub_unit = self.get_sub_units()[sub_unit_index]
            return sub_unit.get_by_address(address=address[1:])
        else:
            return None

    def get_dict(self) -> dict:
        result_dict = {
            'type': type(self).__name__,
            'raw_text': self.get_raw_text(),
            'format_flags': list(map(lambda enum_item: enum_item.value, self.get_format_flags())),
        }

        sub_dict_list = list(map(lambda sub_unit: sub_unit.get_dict(), self.get_sub_units()))
        if len(sub_dict_list) > 0:
            result_dict['sub_units'] = sub_dict_list

        return result_dict


class EmptyUnit(TextUnit):

    def __init__(self):
        super().__init__("")

    def __str__(self):
        return f"{type(self).__name__}"

    def _parse_sub_units(self, raw_text: str) -> list['TextUnit']:
        return []

    def get_raw_text(self) -> str:
        return self.__str__()


class TextSpaceUnit(TextUnit):
    pass


class TextWordUnit(TextUnit):
    pass


class TextWordGroupUnit(TextUnit):

    def __init__(self, sub_units: list[TextUnit]):
        self.__predefined_sub_units = sub_units

        super().__init__(
            raw_text=''.join(map(lambda unit: unit.get_raw_text(), sub_units)),
            format_flags=sub_units[0].get_format_flags(),  # take format flags from the first word
        )

    def get_sub_units(self) -> list['TextUnit']:
        return self.__predefined_sub_units


class TextSubSentenceUnit(TextUnit):

    def _parse_sub_units(self, raw_text: str) -> list['TextUnit']:
        split_regex = r'\S+|\s+'  # words and spaces selector
        words = re.findall(split_regex, raw_text)
        words = list(map(self.__map_sub_unit, enumerate(words)))
        words_and_words_groups = TextSubSentenceUnit.__build_words_and_words_groups(words=words)
        return words_and_words_groups

    def __map_sub_unit(self, enumerated_item) -> TextUnit:
        index = enumerated_item[0]
        value = enumerated_item[1]

        format_flags = []
        if FormatFlag.START_OF_PARAGRAPH in self.get_format_flags() and index == 0:
            format_flags.append(FormatFlag.START_OF_PARAGRAPH)

        if FormatFlag.START_OF_SENTENCE in self.get_format_flags() and index == 0:
            format_flags.append(FormatFlag.START_OF_SENTENCE)

        if len(value.strip()) == 0:
            return TextSpaceUnit(
                raw_text=value,
                format_flags=format_flags,
            )
        else:
            return TextWordUnit(
                raw_text=value,
                format_flags=format_flags,
            )

    @staticmethod
    def get_subarray(array, start_index, count):
        if start_index < 0:
            raise ValueError("start_index must be non-negative")

        # Ensure start_index doesn't exceed array length
        if start_index >= len(array):
            return []

        # Calculate end_index ensuring it doesn't exceed array length
        safe_end_index = min(start_index + count, len(array))
        return array[start_index:safe_end_index]

    @staticmethod
    def __build_words_and_words_groups(words: list['TextUnit']) -> list['TextUnit']:
        group_size = 3
        max_satellite_size = 3
        words_and_word_pairs = []

        group_index = 0

        while group_index < len(words):
            word_group = TextSubSentenceUnit.get_subarray(array=words, start_index=group_index, count=group_size)

            group_first_word = word_group[0]
            group_last_word = word_group[len(word_group) - 1]

            group_full = len(word_group) == group_size
            group_starts_with_space = type(group_first_word) is TextSpaceUnit
            group_ends_with_punctuation = group_last_word.get_raw_text() in string.punctuation
            if not group_full or group_starts_with_space:
                words_and_word_pairs.append(group_first_word)
                group_index = group_index + 1
                continue

            if group_ends_with_punctuation:
                # merge "<word><space><!?>>" into single word
                word_unit = TextWordUnit(
                    raw_text=''.join(map(lambda unit: unit.get_raw_text(), word_group)),
                    format_flags=word_group[0].get_format_flags(),  # take format flags from the first word
                )
                words_and_word_pairs.append(word_unit)
                group_index = group_index + group_size

            elif len(group_first_word.get_raw_text()) <= max_satellite_size:
                group_unit = TextWordGroupUnit(sub_units=word_group)
                words_and_word_pairs.append(group_unit)
                group_index = group_index + group_size  # move index

            else:
                words_and_word_pairs.append(group_first_word)
                group_index = group_index + 1  # move index

        return words_and_word_pairs


class TextSentenceUnit(TextUnit):

    def _parse_sub_units(self, raw_text: str) -> list['TextUnit']:
        split_regex = r'[^,:;.]+(?:,|;|\.{3}|.)?'
        sub_sentences = re.findall(split_regex, raw_text, re.MULTILINE)
        sub_sentences = list(map(self.__map_sub_unit, enumerate(sub_sentences)))
        return sub_sentences

    def __map_sub_unit(self, enumerated_item) -> TextUnit:
        index = enumerated_item[0]
        value = enumerated_item[1]

        format_flags = []
        if FormatFlag.START_OF_PARAGRAPH in self.get_format_flags() and index == 0:
            format_flags.append(FormatFlag.START_OF_PARAGRAPH)

        if FormatFlag.START_OF_SENTENCE in self.get_format_flags() and index == 0:
            format_flags.append(FormatFlag.START_OF_SENTENCE)

        return TextSubSentenceUnit(
            raw_text=value,
            format_flags=format_flags,
        )


class TextParagraphUnit(TextUnit):

    def _parse_sub_units(self, raw_text: str) -> list['TextUnit']:
        # sentences selector
        split_regex = r'([^.!?]*(?:\.\.\.|[.!?])(?=\s|$))'
        sentences = re.findall(split_regex, raw_text)
        sentences = list(map(self.__map_sub_unit, enumerate(sentences)))
        return sentences

    def __map_sub_unit(self, enumerated_item) -> TextUnit:
        index = enumerated_item[0]
        value = enumerated_item[1]

        format_flags = []
        if FormatFlag.START_OF_PARAGRAPH in self.get_format_flags() and index == 0:
            format_flags.append(FormatFlag.START_OF_PARAGRAPH)

        if index == 0:
            format_flags.append(FormatFlag.START_OF_SENTENCE)

        return TextSentenceUnit(
            raw_text=value,
            format_flags=format_flags,
        )


class TextRootUnit(TextUnit):

    def _parse_sub_units(self, raw_text: str) -> list['TextUnit']:
        # paragraphs selector: empty and not
        split_regex = r'.+\n|.+|\n'
        paragraphs = re.findall(split_regex, raw_text)
        paragraphs = list(map(self.__map_sub_unit, enumerate(paragraphs)))
        return paragraphs

    def __map_sub_unit(self, enumerated_item) -> TextUnit:
        index = enumerated_item[0]
        value = enumerated_item[1]

        return TextParagraphUnit(
            raw_text=value.replace('\n', ''),
            format_flags=[FormatFlag.START_OF_PARAGRAPH],  # adding PARAGRAPH flag to each item
        )

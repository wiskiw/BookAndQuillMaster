import re
from enum import Enum
from typing import List, Union
from abc import ABC, abstractmethod


class FormatFlag(Enum):
    PARAGRAPH = 'PARAGRAPH'


class TextUnit(ABC):

    @abstractmethod
    def _parse_sub_units(self, raw_text: str) -> List['TextUnit']:
        pass

    def __init__(self, raw_text: str, format_flags=None):
        if format_flags is None:
            format_flags = []

        self.__raw_text: str = raw_text
        self.__sub_units: List[TextUnit] = self._parse_sub_units(raw_text=raw_text)
        self.__separator = ' '
        self.__format_flags: list[FormatFlag] = format_flags

    def __str__(self):
        return f"{type(self).__name__}({self.__sub_units if self.__sub_units else self.__raw_text})"

    def __repr__(self):
        return str(self)

    def get_raw_text(self) -> str:
        return self.__raw_text

    def get_separator(self) -> str:
        return self.__separator

    def get_format_flags(self) -> list[FormatFlag]:
        return self.__format_flags

    def get_sub_units(self) -> List['TextUnit']:
        return self.__sub_units

    # address = [] - leads to self
    # address = [0] - leads to first sub-unit
    # address = [0, 1] - leads to second sub-unit of self sub-unit
    # if address out or range -> None
    def get_by_address(self, address: List[int]) -> Union['TextUnit', None]:
        if len(address) == 0:
            return self

        sub_unit_index = address[0]
        if sub_unit_index < len(self.__sub_units):
            sub_unit = self.__sub_units[sub_unit_index]
            return sub_unit.get_by_address(address=address[1:])
        else:
            return None

    def get_dict(self) -> dict:
        result_dict = {
            'type': type(self).__name__,
            'raw_text': self.__raw_text,
            'format_flags': list(map(lambda enum_item: enum_item.value, self.__format_flags)),
        }

        sub_dict_list = list(map(lambda sub_unit: sub_unit.get_dict(), self.__sub_units))
        if len(sub_dict_list) > 0:
            result_dict['sub_units'] = sub_dict_list

        return result_dict


class EmptyUnit(TextUnit):

    def __init__(self):
        super().__init__("")

    def __str__(self):
        return f"{type(self).__name__}"

    def _parse_sub_units(self, raw_text: str) -> List['TextUnit']:
        return []

    def get_raw_text(self) -> str:
        return self.__str__()


class TextWordUnit(TextUnit):

    def _parse_sub_units(self, raw_text: str) -> List['TextUnit']:
        # no sub text units for Word
        return []


class TextSubSentenceUnit(TextUnit):

    @staticmethod
    def __mapper(enumerated_item) -> TextUnit:
        index = enumerated_item[0]
        value = enumerated_item[1]

        format_flags = []
        if index == 0:
            format_flags.append(FormatFlag.PARAGRAPH)

        return TextWordUnit(
            raw_text=value,
            format_flags=format_flags,
        )

    def _parse_sub_units(self, raw_text: str) -> List['TextUnit']:
        split_regex = r'\S+'
        words = re.findall(split_regex, raw_text)
        words = list(map(self.__mapper, enumerate(words)))
        return words


class TextSentenceUnit(TextUnit):

    @staticmethod
    def __mapper(enumerated_item) -> TextUnit:
        index = enumerated_item[0]
        value = enumerated_item[1]

        format_flags = []
        if index == 0:
            format_flags.append(FormatFlag.PARAGRAPH)

        return TextSubSentenceUnit(
            raw_text=value.strip(),
            format_flags=format_flags,
        )

    def _parse_sub_units(self, raw_text: str) -> List['TextUnit']:
        split_regex = r'.+?(?:[.,;]|$)'
        sub_sentences = re.findall(split_regex, raw_text, re.MULTILINE)
        sub_sentences = list(map(self.__mapper, enumerate(sub_sentences)))
        return sub_sentences


class TextParagraphUnit(TextUnit):

    @staticmethod
    def __mapper(enumerated_item) -> TextUnit:
        index = enumerated_item[0]
        value = enumerated_item[1]

        format_flags = []
        if index == 0:
            format_flags.append(FormatFlag.PARAGRAPH)

        return TextSentenceUnit(
            raw_text=value.strip(),
            format_flags=format_flags,
        )

    def _parse_sub_units(self, raw_text: str) -> List['TextUnit']:
        # sentences selector
        split_regex = r'([^.!?]*(?:\.\.\.|[.!?])(?=\s|$))'
        sentences = re.findall(split_regex, raw_text)
        sentences = list(map(self.__mapper, enumerate(sentences)))
        return sentences


class TextRootUnit(TextUnit):

    @staticmethod
    def __mapper(enumerated_item) -> TextUnit:
        index = enumerated_item[0]
        value = enumerated_item[1]

        return TextParagraphUnit(
            raw_text=value.strip(),
            format_flags=[FormatFlag.PARAGRAPH], # adding PARAGRAPH flag to each item
        )

    def _parse_sub_units(self, raw_text: str) -> List['TextUnit']:
        # paragraphs selector
        split_regex = r'.+\n|.+'
        paragraphs = re.findall(split_regex, raw_text)
        paragraphs = list(map(self.__mapper, enumerate(paragraphs)))
        return paragraphs

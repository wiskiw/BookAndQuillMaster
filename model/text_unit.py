import re
from enum import Enum
from typing import List, Union
from abc import ABC, abstractmethod


class FormatFlag(Enum):
    START_OF_PARAGRAPH = 'START_OF_PARAGRAPH'
    START_OF_SENTENCE = 'START_OF_SENTENCE'
    REQUESTED_NEW_PAGE = 'START_OF_PAGE'


FORMAT_FLAG_TAGS = {
    FormatFlag.REQUESTED_NEW_PAGE: '{{$new_page}}',
}


class TextUnit(ABC):

    def __init__(self, raw_text: str, format_flags: list[FormatFlag] = None):
        if format_flags is None:
            format_flags = []

        self.__raw_text: str = raw_text
        self.__format_flags: list[FormatFlag] = format_flags
        self.__sub_units: list[TextUnit] = self._create_sub_units(raw_text=raw_text)

    def __str__(self):
        return f"{type(self).__name__}({self.__sub_units if self.__sub_units else self.__raw_text})"

    def __repr__(self):
        return str(self)

    @abstractmethod
    def _create_sub_units(self, raw_text: str) -> list['TextUnit']:
        pass

    def get_sub_units(self) -> list['TextUnit']:
        return self.__sub_units

    def get_raw_text(self) -> str:
        return self.__raw_text

    def get_format_flags(self) -> list[FormatFlag]:
        return self.__format_flags

    def has_format_flag(self, format_flag: FormatFlag) -> bool:
        return format_flag in self.get_format_flags()

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

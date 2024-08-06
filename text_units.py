import re
from typing import List, Union
from abc import ABC, abstractmethod


class TextUnit(ABC):

    @abstractmethod
    def _parse_sub_units(self, raw_text: str) -> List['TextUnit']:
        pass

    def __init__(self, raw_text: str):
        self.__raw_text: str = raw_text
        self.__sub_units: List[TextUnit] = self._parse_sub_units(raw_text=raw_text)

    def __str__(self):
        return f"{type(self).__name__}({self.__sub_units if self.__sub_units else self.__raw_text})"

    def __repr__(self):
        return str(self)

    def get_raw_text(self) -> str:
        return self.__raw_text

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

    def _parse_sub_units(self, raw_text: str) -> List['TextUnit']:
        split_regex = r'\S+'
        groups = re.findall(split_regex, raw_text)
        groups = list(map(lambda item: TextWordUnit(raw_text=item), groups))
        return groups


class TextSentenceUnit(TextUnit):

    def _parse_sub_units(self, raw_text: str) -> List['TextUnit']:
        split_regex = r'.+?(?:[.,;]|$)'
        groups = re.findall(split_regex, raw_text)
        groups = list(map(lambda item: item.strip(), groups))
        groups = list(map(lambda item: TextSubSentenceUnit(raw_text=item), groups))
        return groups


class TextParagraphUnit(TextUnit):

    def _parse_sub_units(self, raw_text: str) -> List['TextUnit']:
        # sentences selector
        split_regex = r'([^.!?]*(?:\.\.\.|[.!?])(?=\s|$))'

        groups = re.findall(split_regex, raw_text)
        groups = list(map(lambda item: item.strip(), groups))
        groups = list(map(lambda item: TextSentenceUnit(raw_text=item), groups))
        return groups


class TextRootUnit(TextUnit):

    def _parse_sub_units(self, raw_text: str) -> List['TextUnit']:
        # paragraphs selector
        split_regex = r'.+\n|.+'

        groups = re.findall(split_regex, raw_text)
        groups = list(map(lambda item: item.strip(), groups))
        groups = list(map(lambda item: TextParagraphUnit(raw_text=item), groups))
        return groups

import re

from model.text_paragraph_unit import TextParagraphUnit
from model.text_unit import TextUnit, FormatFlag


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

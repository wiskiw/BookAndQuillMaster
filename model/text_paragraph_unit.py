import re

from model.text_sentence_unit import TextSentenceUnit
from model.text_unit import TextUnit, FormatFlag


class TextParagraphUnit(TextUnit):

    def _parse_sub_units(self, raw_text: str) -> list[TextUnit]:
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

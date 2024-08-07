import re

from model.text_sub_sentence_unit import TextSubSentenceUnit
from model.text_unit import TextUnit, FormatFlag


class TextSentenceUnit(TextUnit):

    def _parse_sub_units(self, raw_text: str) -> list[TextUnit]:
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

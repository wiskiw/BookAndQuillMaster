import re

from bookmaster.model.text_sub_sentence_unit import TextSubSentenceUnit
from bookmaster.model.text_unit import TextUnit, FormatFlag, FORMAT_FLAG_TAGS
from other.utils import map_indexed


class TextSentenceUnit(TextUnit):

    def __init__(self, raw_text: str, format_flags: list[FormatFlag] = None):
        parent_format_flags = format_flags if format_flags is not None else []
        self_format_flags = [FormatFlag.START_OF_SENTENCE]  # adding START_OF_SENTENCE flag to each sentence unit

        super().__init__(
            raw_text=raw_text,
            format_flags=parent_format_flags + self_format_flags,
        )

    def _create_sub_units(self, raw_text: str) -> list['TextUnit']:
        split_regex = r'[^,:;.]+(?:,|;|\.{3}|.)?'
        sub_sentences = re.findall(split_regex, raw_text, re.MULTILINE)
        sub_sentences = map_indexed(self.__map_sub_unit, sub_sentences)
        return sub_sentences

    def __map_sub_unit(self, index: int, value: str) -> TextUnit:
        parent_format_flags = []
        first_sub_unit = index == 0

        if first_sub_unit and self.has_format_flag(FormatFlag.START_OF_PARAGRAPH):
            parent_format_flags.append(FormatFlag.START_OF_PARAGRAPH)

        if first_sub_unit and self.has_format_flag(FormatFlag.START_OF_SENTENCE):
            parent_format_flags.append(FormatFlag.START_OF_SENTENCE)

        if first_sub_unit and self.has_format_flag(FormatFlag.REQUESTED_NEW_PAGE):
            parent_format_flags.append(FormatFlag.REQUESTED_NEW_PAGE)

        return TextSubSentenceUnit(
            raw_text=value,
            format_flags=parent_format_flags,
        )

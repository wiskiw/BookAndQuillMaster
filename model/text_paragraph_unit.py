import re

from model.text_sentence_unit import TextSentenceUnit
from model.text_unit import TextUnit, FormatFlag, FORMAT_FLAG_TAGS
from utils import map_indexed


class TextParagraphUnit(TextUnit):

    def __init__(self, raw_text: str, format_flags: list[FormatFlag] = None):
        parent_format_flags = format_flags if format_flags is not None else []
        self_format_flags = [FormatFlag.START_OF_PARAGRAPH]  # adding PARAGRAPH flag to each paragraph unit

        super().__init__(
            raw_text=raw_text,
            format_flags=parent_format_flags + self_format_flags,
        )

    def _create_sub_units(self, raw_text: str) -> list['TextUnit']:
        # sentences selector
        split_regex = r'([^.!?]*(?:\.\.\.|[.!?]|))'
        sentences = re.findall(split_regex, raw_text)
        sentences = map_indexed(self.__map_sub_unit, sentences)
        return sentences

    def __map_sub_unit(self, index: int, value: str) -> TextUnit:
        parent_format_flags = []
        first_sub_unit = index == 0

        if first_sub_unit and self.has_format_flag(FormatFlag.START_OF_PARAGRAPH):
            parent_format_flags.append(FormatFlag.START_OF_PARAGRAPH)

        if first_sub_unit and self.has_format_flag(FormatFlag.REQUESTED_NEW_PAGE):
            parent_format_flags.append(FormatFlag.REQUESTED_NEW_PAGE)

        return TextSentenceUnit(
            raw_text=value,
            format_flags=parent_format_flags,
        )

    def _create_sub_unit_flags(self, sub_index: int, sub_text: str) -> list[FormatFlag]:
        format_flags = [
            FormatFlag.START_OF_SENTENCE,  # adding START_OF_SENTENCE flag to each sub unit
        ]

        first_sub_unit = sub_index == 0
        if first_sub_unit and self.has_format_flag(FormatFlag.START_OF_PARAGRAPH):
            format_flags.append(FormatFlag.START_OF_PARAGRAPH)

        self_has_new_page_flag = self.has_format_flag(FormatFlag.REQUESTED_NEW_PAGE)
        sub_text_has_tag_flag = sub_text.strip().startswith(FORMAT_FLAG_TAGS[FormatFlag.REQUESTED_NEW_PAGE])
        if (first_sub_unit and self_has_new_page_flag) or sub_text_has_tag_flag:
            format_flags.append(FormatFlag.REQUESTED_NEW_PAGE)

        return format_flags

    def _remove_flag_tags_from_sub_text(self, flags: list[FormatFlag], sub_text: str) -> str:
        if FormatFlag.REQUESTED_NEW_PAGE in flags:
            flag_tag_new_page = FORMAT_FLAG_TAGS[FormatFlag.REQUESTED_NEW_PAGE]
            sub_text = sub_text.replace(flag_tag_new_page, '')

        return sub_text

import re

from model.text_paragraph_unit import TextParagraphUnit
from model.text_unit import TextUnit, FormatFlag, FORMAT_FLAG_TAGS
from utils import map_indexed


# Contains tags and text segment
class TextTaggedUnit(TextUnit):

    def __init__(self, raw_text: str, format_flags: list[FormatFlag] = None, text_tags: list[str] = None):
        parent_format_flags = format_flags if format_flags is not None else []
        self_format_flags = TextTaggedUnit.__get_format_flag_list_by_text_tags(text_tags) if text_tags is not None \
            else []

        super().__init__(
            raw_text=raw_text,
            format_flags=parent_format_flags + self_format_flags,
        )
        self.__text_tags = text_tags

    def _create_sub_units(self, raw_text: str) -> list[TextUnit]:
        # paragraphs selector: empty and not
        split_regex = r'.+\n|.+|\n'
        paragraphs = re.findall(split_regex, raw_text)
        paragraphs = map_indexed(self.__map_sub_unit, paragraphs)
        return paragraphs

    def __map_sub_unit(self, index: int, value: str) -> TextUnit:
        parent_format_flags = []
        first_sub_unit = index == 0

        if first_sub_unit and self.has_format_flag(FormatFlag.REQUESTED_NEW_PAGE):
            parent_format_flags.append(FormatFlag.REQUESTED_NEW_PAGE)

        return TextParagraphUnit(
            raw_text=value,
            format_flags=parent_format_flags,
        )

    @staticmethod
    def __get_format_flag_list_by_text_tags(text_tag_list: list[str]) -> list[FormatFlag]:
        return list(map(TextTaggedUnit.__get_format_flag_by_text_tag, text_tag_list))

    @staticmethod
    def __get_format_flag_by_text_tag(text_tag: str) -> FormatFlag:
        for format_flag, tag in FORMAT_FLAG_TAGS.items():
            if text_tag == tag:
                return format_flag

        raise Exception(f"Unknown text tag '{text_tag}'. Please add to mapping.")

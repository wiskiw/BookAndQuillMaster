import re
from dataclasses import dataclass

from bookmaster.model.text_tagged_unit import TextTaggedUnit
from bookmaster.model.text_unit import TextUnit
from other.utils import map_indexed


class TextRootUnit(TextUnit):

    def _create_sub_units(self, raw_text: str) -> list['TextUnit']:
        tag_regex = r'(\{\{\$[^}]*\}\})'

        texts_and_tags_list = re.split(tag_regex, raw_text, flags=re.MULTILINE)

        tagged_text_list = []
        tags = []
        for text_or_tag in texts_and_tags_list:
            if len(text_or_tag) == 0:
                continue

            if re.fullmatch(tag_regex, text_or_tag):
                # tag
                tags.append(text_or_tag)
            else:
                # text
                tagged_text = TaggedText(text=text_or_tag, tags=tags)
                tagged_text_list.append(tagged_text)
                tags = []

        tagged_units = map_indexed(TextRootUnit.__map_sub_unit, tagged_text_list)
        return tagged_units

    @staticmethod
    def __map_sub_unit(index: int, value: 'TaggedText') -> TextUnit:
        return TextTaggedUnit(raw_text=value.text, text_tags=value.tags)


@dataclass
class TaggedText:
    text: str
    tags: list[str]

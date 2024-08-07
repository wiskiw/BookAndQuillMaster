import re

from model.text_unit import FormatFlag
from model.text_word_unit import TextWordUnit


class TextSpaceUnit(TextWordUnit):
    __NOT_EMPTY_SPACE_CHARACTERS_REGEX_SELECTOR = r'\s+'

    def __init__(self, raw_text: str, format_flags: list[FormatFlag] = None):
        if not re.fullmatch(self.__NOT_EMPTY_SPACE_CHARACTERS_REGEX_SELECTOR, raw_text):
            raise Exception(
                f"{type(self).__name__} raw_text must contains only space characters and must not be empty. "
                f"Actual raw_text='{raw_text}'",
            )

        super().__init__(raw_text, format_flags)

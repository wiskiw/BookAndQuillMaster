from bookmaster.model.text_unit import TextUnit, FormatFlag


class TextWordUnit(TextUnit):

    def __init__(self, raw_text: str, format_flags: list[FormatFlag] = None):
        super().__init__(raw_text, format_flags)

        self.__raw_text: str = raw_text

    def _create_sub_units(self, raw_text: str) -> list[TextUnit]:
        # do not support sub units
        return []

    def get_raw_text(self) -> str:
        return self.__raw_text

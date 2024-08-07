from model.text_unit import TextUnit


class TextWordGroupUnit(TextUnit):

    def __init__(self, sub_units: list[TextUnit]):
        self.__predefined_sub_units = sub_units

        super().__init__(
            raw_text=''.join(map(lambda unit: unit.get_raw_text(), sub_units)),
            format_flags=sub_units[0].get_format_flags(),  # take format flags from the first word
        )

    def get_sub_units(self) -> list['TextUnit']:
        return self.__predefined_sub_units

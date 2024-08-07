from model.text_unit import TextUnit


class TextEmptyUnit(TextUnit):

    def __init__(self):
        super().__init__("")

    def __str__(self):
        return f"{type(self).__name__}"

    def _parse_sub_units(self, raw_text: str) -> list['TextUnit']:
        return []

    def get_raw_text(self) -> str:
        return self.__str__()

from bookmaster.model.text_unit import TextUnit
from bookmaster.model.text_word_unit import TextWordUnit


class TextEmptyUnit(TextWordUnit):

    def __init__(self):
        super().__init__("")

    def __str__(self):
        return f"{type(self).__name__}"

    def _create_sub_units(self, raw_text: str) -> list[TextUnit]:
        return []

    def get_raw_text(self) -> str:
        return self.__str__()

from bookmaster.model.text_unit import TextUnit


class TextWordUnit(TextUnit):

    def _create_sub_units(self, raw_text: str) -> list[TextUnit]:
        # do not support sub units
        return []

import copy
from abc import ABC, abstractmethod

from text_unit_reader import TextUnitReader
from text_units import TextUnit, EmptyUnit


class McCharRuler:
    char_to_width_dict: dict[str, int]

    def __init__(self, char_to_width_dict: dict[str, int]):
        self.char_to_width_dict = char_to_width_dict

    def get_width(self, text: str):
        if len(text) == 0:
            return 0

        text_width = 0
        between_chars_width = 1

        for char in text:
            char_width = self.char_to_width_dict[char]
            text_width += char_width + between_chars_width
        return text_width - between_chars_width


class TextContainer(ABC):

    @abstractmethod
    def try_append(self, text_unit: TextUnit) -> bool:
        pass

    @abstractmethod
    def get_text(self) -> str:
        pass


class McLine(TextContainer):

    def __init__(self, ruler: McCharRuler, text: str = ""):
        super().__init__()

        self.__text = text
        self.__max_width_px = 114
        self.__ruler = ruler

    def __can_append(self, text_unit: TextUnit) -> bool:
        # use temporary object to check if text will fit after merging
        temp_mc_line = copy.deepcopy(self)
        temp_mc_line.__append(text_unit)
        merged_text_width_px = self.__ruler.get_width(temp_mc_line.__text)

        return merged_text_width_px <= self.__max_width_px

    def __append(self, text_unit: TextUnit):
        if len(self.__text) == 0:
            self.__text = text_unit.get_raw_text()
        else:
            separator = text_unit.get_separator()
            self.__text = separator.join([self.__text, text_unit.get_raw_text()])

    def try_append(self, text_unit: TextUnit) -> bool:
        if self.__can_append(text_unit=text_unit):
            self.__append(text_unit=text_unit)
            return True
        else:
            return False

    def get_text(self) -> str:
        return self.__text


class McPage(TextContainer):

    def __init__(self, ruler: McCharRuler):
        super().__init__()

        self.__lines: list[McLine] = []
        self.__max__line_number = 14
        self.__ruler = ruler

    def try_append(self, text_unit: TextUnit) -> bool:
        if len(self.__lines) > 0:
            last_line = self.__lines[len(self.__lines) - 1]

            if last_line.try_append(text_unit):
                # text unit fits into the last existing  line
                return True

        if len(self.__lines) <= self.__max__line_number:
            # page not full, adding a new line
            new_line = McLine(ruler=self.__ruler)

            if new_line.try_append(text_unit):
                # text was added into the new line
                # adding line to the page
                # self.__current_line_index = self.__current_line_index + 1
                self.__lines.append(new_line)
                return True
            else:
                # text not fit even in a new line
                return False

    def get_text(self) -> str:
        line_text = map(lambda line: line.get_text(), self.__lines)
        return '\n'.join(line_text)


class TextContainerWriter:

    def __init__(self, reader: TextUnitReader, ruler: McCharRuler):
        self.__reader = reader
        self.__ruler = ruler

    def write(self) -> TextContainer:
        text_container = McPage(ruler=self.__ruler)

        deep_factor = 0
        while True:
            text_unit = self.__reader.read_next(deep_factor=deep_factor)

            if type(text_unit) is EmptyUnit:
                # no more units that would fit into this text container
                break

            was_appended = text_container.try_append(text_unit=text_unit)
            if was_appended:
                self.__reader.consume_next(deep_factor=deep_factor)
                deep_factor = 0
                continue

            deep_factor = deep_factor + 1

        return text_container

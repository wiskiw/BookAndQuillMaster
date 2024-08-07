import copy
from abc import ABC, abstractmethod

from text_unit_reader import TextUnitReader
from text_units import TextUnit, EmptyUnit, FormatFlag


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
    def get_pretty_str(self) -> str:
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

    def get_pretty_str(self) -> str:
        return self.__text

    def get_text(self) -> str:
        return self.__text


class McPage(TextContainer):

    def __init__(self, ruler: McCharRuler):
        super().__init__()

        self.__lines: list[McLine] = []
        self.__max_line_number = 14
        self.__ruler = ruler

    def try_append(self, text_unit: TextUnit) -> bool:
        new_line_required = FormatFlag.START_OF_PARAGRAPH in text_unit.get_format_flags()

        if not new_line_required and len(self.__lines) > 0:
            # attempt to append to the last existing line
            last_line = self.__lines[len(self.__lines) - 1]

            if last_line.try_append(text_unit):
                # text unit fits into the last existing line
                return True

        if len(self.__lines) <= self.__max_line_number:
            # page is not full, adding a new line
            new_line = McLine(ruler=self.__ruler)

            if new_line.try_append(text_unit):
                # text was added into the new line
                # adding line to the page
                self.__lines.append(new_line)
                return True
            else:
                # text not fit even in a new line
                return False

    def get_pretty_str(self) -> str:
        str_lines = []
        for enumerated_line in enumerate(self.__lines):
            index = enumerated_line[0]
            mc_line = enumerated_line[1]
            str_lines.append(f"{index}: {mc_line.get_pretty_str()}")

        return '\n'.join(str_lines)

    def get_lines(self) -> list[McLine]:
        return self.__lines


class McBook(TextContainer):

    def __init__(self, ruler: McCharRuler):
        super().__init__()

        self.__pages: list[McPage] = []
        self.__max_page_number = 100
        self.__ruler = ruler

    def try_append(self, text_unit: TextUnit) -> bool:
        if len(self.__pages) > 0:
            # attempt to append to the last existing page
            last_page = self.__pages[len(self.__pages) - 1]

            if last_page.try_append(text_unit):
                # text unit fits into the last existing page
                return True

        if len(self.__pages) <= self.__max_page_number:
            # book is not full, adding a new page
            new_page = McPage(ruler=self.__ruler)

            if new_page.try_append(text_unit):
                # text was added into the new page
                # adding page to the book
                self.__pages.append(new_page)
                return True
            else:
                # text not fit even in a new line
                return False

    def get_pretty_str(self) -> str:
        str_pages = []
        for enumerated_page in enumerate(self.__pages):
            index = enumerated_page[0]
            mc_page = enumerated_page[1]
            str_pages.append(f" -------- Page {index} -------- \n" + mc_page.get_pretty_str())

        return '\n\n'.join(str_pages)

    def get_pages(self) -> list[McPage]:
        return self.__pages


class TextContainerWriter:

    def __init__(self, reader: TextUnitReader, ruler: McCharRuler):
        self.__reader = reader
        self.__ruler = ruler

    def write(self) -> TextContainer:
        text_container = McBook(ruler=self.__ruler)

        deep_factor = 0
        while True:
            text_unit = self.__reader.read_next(deep_factor=deep_factor)

            if type(text_unit) is EmptyUnit:
                # no more units that would fit into this text container
                text_unit = self.__reader.read_next(deep_factor=deep_factor - 1)
                print(f"WARNING some text wasn't added: '{text_unit.get_raw_text()}'")
                break

            was_appended = text_container.try_append(text_unit=text_unit)
            if was_appended:
                self.__reader.consume_next(deep_factor=deep_factor)
                deep_factor = 0
                continue

            deep_factor = deep_factor + 1

        return text_container

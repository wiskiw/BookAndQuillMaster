import copy

from bookmaster.book_writing_config import BookWritingConfig
from bookmaster.character_ruler import McCharRuler
from bookmaster.model.text_sentence_unit import TextSentenceUnit
from bookmaster.model.text_sub_sentence_unit import TextSubSentenceUnit
from bookmaster.model.text_unit import TextUnit, FormatFlag


class McLine:

    def __init__(self, ruler: McCharRuler, writing_config: BookWritingConfig):
        super().__init__()

        self.__text_units = []
        self.__writing_config = writing_config
        self.__max_width_px = 114
        self.__ruler = ruler

    def __can_append(self, text_unit: TextUnit) -> bool:
        # use temporary object to check if text will fit after merging
        temp_line = copy.deepcopy(self)
        temp_line.__append(text_unit)
        merged_text_width_px = self.__ruler.get_width_of_text_units(temp_line.get_text_units())

        return merged_text_width_px <= self.__max_width_px

    def __append(self, text_unit: TextUnit):
        self.__text_units.append(text_unit)

    def try_append(self, text_unit: TextUnit) -> bool:
        if self.__can_append(text_unit=text_unit):
            self.__append(text_unit=text_unit)
            return True
        else:
            return False

    def get_text(self) -> str:
        if len(self.__text_units) == 0:
            return ""

        # ignoring right spacings
        unit_text_list = list(map(lambda unit: unit.get_raw_text(), self.__text_units))
        line_text = ''.join(unit_text_list).rstrip()

        first_unit = self.__text_units[0]
        start_of_paragraph = first_unit.has_format_flag(FormatFlag.START_OF_PARAGRAPH)
        if not start_of_paragraph:
            # ignoring left spacings it the line is not beginning of paragraph
            line_text = line_text.lstrip()

        return line_text

    def get_text_units(self) -> list[TextUnit]:
        return self.__text_units


class McPage:

    def __init__(self, ruler: McCharRuler, writing_config: BookWritingConfig):
        super().__init__()

        self.__writing_config = writing_config
        self.__lines: list[McLine] = []
        self.__max_line_number = 14
        self.__ruler = ruler

    def try_append(self, text_unit: TextUnit) -> bool:
        if not self.is_config_allow(text_unit):
            return False

        new_line_required = text_unit.has_format_flag(FormatFlag.START_OF_PARAGRAPH)

        if not new_line_required and len(self.__lines) > 0:
            # page not empty, trying to append to the last existing line
            last_line = self.__lines[len(self.__lines) - 1]

            if last_line.try_append(text_unit):
                # text unit fits into the last existing line
                return True

        if len(self.__lines) < self.__max_line_number:
            # page is not full, adding a new line
            new_line = McLine(ruler=self.__ruler, writing_config=self.__writing_config)

            if new_line.try_append(text_unit):
                # text was added into the new line
                # adding line to the page
                self.__lines.append(new_line)
                return True
            else:
                # text not fit even in a new line
                return False

        return False

    def is_config_allow(self, text_unit: TextUnit) -> bool:
        last_line_exist = len(self.__lines) == self.__max_line_number
        adding_last_line = len(self.__lines) == self.__max_line_number - 1
        start_of_sentence = text_unit.has_format_flag(FormatFlag.START_OF_SENTENCE)
        sentence_or_sub_sentence_unit = type(text_unit) is TextSentenceUnit or type(text_unit) is TextSubSentenceUnit

        if (last_line_exist and not self.__writing_config.allow_new_sentence_on_the_last_line
                and start_of_sentence and not sentence_or_sub_sentence_unit):
            # aborting attempt of adding a start of sentences unit (if it's not a whole sentence/sub-sentence)
            # to existing last line
            # skip sentence or sub-sentence to allow adding to the last line, if the whole sentence fits
            return False

        if (adding_last_line and not self.__writing_config.allow_new_sentence_on_the_last_line
                and start_of_sentence and not sentence_or_sub_sentence_unit):
            # aborting attempt of adding a start of sentences unit (if it's not a whole sentence/sub-sentence)
            # to a new last line
            # skip sentence or sub-sentence to allow adding to the last line, if the whole sentence fits
            return False

        return True

    def get_lines(self) -> list[McLine]:
        return self.__lines


class McBook:

    def __init__(self, ruler: McCharRuler, writing_config: BookWritingConfig):
        super().__init__()

        self.__writing_config = writing_config
        self.__title = None
        self.__pages: list[McPage] = []
        self.__max_page_number = 100
        self.__ruler = ruler

    def set_title(self, title: str):
        self.__title = title

    def get_title(self) -> str:
        return self.__title

    def try_append(self, text_unit: TextUnit) -> bool:
        if text_unit.has_format_flag(FormatFlag.IGNORE_UNIT):
            return False

        new_page_required = text_unit.has_format_flag(FormatFlag.REQUESTED_NEW_PAGE)

        if len(self.__pages) > 0 and not new_page_required:
            # attempt to append to the last existing page
            last_page = self.__pages[len(self.__pages) - 1]

            if last_page.try_append(text_unit):
                # text unit fits into the last existing page
                return True

        if len(self.__pages) < self.__max_page_number:
            # book is not full, adding a new page
            new_page = McPage(ruler=self.__ruler, writing_config=self.__writing_config)

            if new_page.try_append(text_unit):
                # text was added into the new page
                # adding page to the book
                self.__pages.append(new_page)
                return True
            else:
                # text not fit even in a new line
                return False

        return False

    def get_pages(self) -> list[McPage]:
        return self.__pages

    def get_page(self, index: int) -> McPage | None:
        if index < 0 or index >= self.__max_page_number:
            raise Exception(f'Page index is out of border. Available range 0<=index<{self.__max_page_number}')

        return self.__pages[index] if index < len(self.__pages) else None

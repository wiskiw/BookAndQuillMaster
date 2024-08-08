from bookmaster.book_writing_config import BookWritingConfig
from bookmaster.character_ruler import McCharRuler
from bookmaster.model.text_empty_unit import TextEmptyUnit
from bookmaster.text_container import McBook
from bookmaster.text_unit_reader import TextUnitReader

_DEFAULT_CONFIG = BookWritingConfig(
    allow_new_sentence_on_the_last_line=False,
)


class BookWriter:

    def __init__(self, reader: TextUnitReader, ruler: McCharRuler, config: BookWritingConfig = _DEFAULT_CONFIG):
        self.__reader = reader
        self.__ruler = ruler
        self.__config = config

    def write(self) -> McBook:
        text_container = McBook(ruler=self.__ruler, writing_config=self.__config)

        deep_factor = 0
        while True:
            text_unit = self.__reader.read_next(deep_factor=deep_factor)

            if type(text_unit) is TextEmptyUnit:
                # no more units that would fit into this text container
                text_unit = self.__reader.read_next(deep_factor=deep_factor - 1)
                if type(text_unit) is not TextEmptyUnit:
                    print(f"WARNING some text wasn't added: '{text_unit.get_raw_text()}'")
                    raise ValueError(f"WARNING some text wasn't added: '{text_unit.get_raw_text()}'")
                break

            was_appended = text_container.try_append(text_unit=text_unit)
            if was_appended:
                self.__reader.consume_next(deep_factor=deep_factor)
                deep_factor = 0
                continue

            deep_factor = deep_factor + 1

        return text_container

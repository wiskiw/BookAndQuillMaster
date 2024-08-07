from bookmaster.model.text_empty_unit import TextEmptyUnit
from bookmaster.model.text_unit import TextUnit


class TextUnitReader:

    def __init__(self, text_unit: TextUnit):
        self.__text_unit = text_unit
        self.__read_address = []
        self.__reading_complete = False

    def __get_next_available_address_recursively(self, text_unit: TextUnit, address: list[int]) -> list[int] | None:
        if len(address) == 0:
            return None

        last_address_index = len(address) - 1
        last_address_value = address[last_address_index]

        next_address = address
        next_address[last_address_index] = last_address_value + 1

        unit_by_next_address = text_unit.get_by_address(next_address)
        if unit_by_next_address is not None:
            return next_address
        else:
            return self.__get_next_available_address_recursively(text_unit, address[:len(address) - 1])

    def __get_next_available_address(self, address: list[int]) -> list[int] | None:
        return self.__get_next_available_address_recursively(text_unit=self.__text_unit, address=address)

    def __scale_read_address(self, deep_factor: int = 0) -> list[int]:
        return self.__read_address + ([0] * deep_factor)

    def read_next(self, deep_factor: int = 0) -> TextUnit:
        return self.__consume_next(update_address=False, deep_factor=deep_factor)

    def consume_next(self, deep_factor: int = 0) -> TextUnit:
        return self.__consume_next(update_address=True, deep_factor=deep_factor)

    def __consume_next(self, update_address: bool = False, deep_factor: int = 0) -> TextUnit:
        if self.__reading_complete:
            return TextEmptyUnit()

        scaled_read_address = self.__scale_read_address(deep_factor=deep_factor)
        targeted_text_unit = self.__text_unit.get_by_address(address=scaled_read_address)

        if not update_address:
            # debug line
            # print(f"scaled_read_address={scaled_read_address}:{targeted_text_unit.get_raw_text() if targeted_text_unit is not None else None}")
            pass

        if update_address and targeted_text_unit is not None:
            next_read_address = self.__get_next_available_address(address=scaled_read_address)

            if next_read_address is not None:
                self.__read_address = next_read_address
            else:
                # no more units
                self.__reading_complete = True
                pass

        return targeted_text_unit if targeted_text_unit is not None else TextEmptyUnit()

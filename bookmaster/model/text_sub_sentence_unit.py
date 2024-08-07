import re
import string

from bookmaster.model.text_space_unit import TextSpaceUnit
from bookmaster.model.text_unit import TextUnit, FormatFlag
from other.utils import map_indexed, get_subarray
from bookmaster.model.text_word_group_unit import TextWordGroupUnit
from bookmaster.model.text_word_unit import TextWordUnit


class TextSubSentenceUnit(TextUnit):

    def _create_sub_units(self, raw_text: str) -> list['TextUnit']:
        split_regex = r'\S+|\s+'  # words and spaces selector
        words = re.findall(split_regex, raw_text)
        words = map_indexed(self.__map_sub_unit, words)
        words_and_words_groups = TextSubSentenceUnit.__build_words_and_words_groups(words=words)
        return words_and_words_groups

    def __map_sub_unit(self, index: int, value: str) -> TextUnit:
        parent_format_flags = []
        first_sub_unit = index == 0

        if first_sub_unit and self.has_format_flag(FormatFlag.START_OF_PARAGRAPH):
            parent_format_flags.append(FormatFlag.START_OF_PARAGRAPH)

        if first_sub_unit and self.has_format_flag(FormatFlag.START_OF_SENTENCE):
            parent_format_flags.append(FormatFlag.START_OF_SENTENCE)

        if first_sub_unit and self.has_format_flag(FormatFlag.REQUESTED_NEW_PAGE):
            parent_format_flags.append(FormatFlag.REQUESTED_NEW_PAGE)

        if len(value.strip()) == 0:
            return TextSpaceUnit(
                raw_text=value,
                format_flags=parent_format_flags,
            )
        else:
            return TextWordUnit(
                raw_text=value,
                format_flags=parent_format_flags,
            )

    @staticmethod
    def __build_words_and_words_groups(words: list[TextUnit]) -> list[TextUnit]:
        group_size = 3
        max_satellite_size = 3
        words_and_word_pairs = []

        group_index = 0

        while group_index < len(words):
            word_group = get_subarray(array=words, start_index=group_index, count=group_size)

            group_first_word = word_group[0]
            group_last_word = word_group[len(word_group) - 1]

            group_full = len(word_group) == group_size
            group_starts_with_space = type(group_first_word) is TextSpaceUnit
            group_ends_with_punctuation = group_last_word.get_raw_text() in string.punctuation
            if not group_full or group_starts_with_space:
                words_and_word_pairs.append(group_first_word)
                group_index = group_index + 1
                continue

            if group_ends_with_punctuation:
                # merge "<word><space><!?>>" into single word
                word_unit = TextWordUnit(
                    raw_text=''.join(map(lambda unit: unit.get_raw_text(), word_group)),
                    format_flags=word_group[0].get_format_flags(),  # take format flags from the first word
                )
                words_and_word_pairs.append(word_unit)
                group_index = group_index + group_size

            elif len(group_first_word.get_raw_text()) <= max_satellite_size:
                group_unit = TextWordGroupUnit(sub_units=word_group)
                words_and_word_pairs.append(group_unit)
                group_index = group_index + group_size  # move index

            else:
                words_and_word_pairs.append(group_first_word)
                group_index = group_index + 1  # move index

        return words_and_word_pairs

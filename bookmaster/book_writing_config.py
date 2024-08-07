from dataclasses import dataclass


@dataclass
class BookWritingConfig:
    allow_new_sentence_on_the_last_line: bool
